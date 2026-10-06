import asyncio
from collections.abc import AsyncGenerator
from datetime import time
import pytest
import pytest_asyncio
from httpx import AsyncClient, ASGITransport
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker, create_async_engine
from sqlalchemy.pool import StaticPool

from app.main import app
from app.core.database import get_db
from app.domain.models.base import Base
from app.domain.models.establishment import Establishment
from app.domain.models.user import User, UserRole
from app.domain.models.service import Service
from app.domain.models.professional import (
    Professional,
    ProfessionalService,
    ProfessionalWorkingHour,
)
from app.domain.models.customer import Customer
from app.core.security import get_password_hash, create_access_token
from app.workers.celery_app import celery_app

# Configura Celery para rodar em memória instantaneamente nos testes sem aguardar broker Redis
celery_app.conf.update(task_always_eager=True, task_eager_propagates=True)

# Engine SQLite Assíncrono em Memória isolado para testes
TEST_DATABASE_URL = "sqlite+aiosqlite:///:memory:"

test_engine = create_async_engine(
    TEST_DATABASE_URL,
    connect_args={"check_same_thread": False},
    poolclass=StaticPool,
)

TestingSessionLocal = async_sessionmaker(
    bind=test_engine,
    class_=AsyncSession,
    autocommit=False,
    autoflush=False,
    expire_on_commit=False,
)


@pytest_asyncio.fixture(scope="function")
async def db_session() -> AsyncGenerator[AsyncSession, None]:
    """Cria tabelas em memória e fornece sessão limpa para cada teste."""
    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.create_all)

    async with TestingSessionLocal() as session:
        yield session

    async with test_engine.begin() as conn:
        await conn.run_sync(Base.metadata.drop_all)


@pytest_asyncio.fixture(scope="function")
async def client(db_session: AsyncSession) -> AsyncGenerator[AsyncClient, None]:
    """Cliente HTTP assíncrono httpx com injeção de sessão assíncrona por request."""
    async def override_get_db() -> AsyncGenerator[AsyncSession, None]:
        async with TestingSessionLocal() as session:
            try:
                yield session
            except Exception:
                await session.rollback()
                raise
            finally:
                await session.close()

    app.dependency_overrides[get_db] = override_get_db
    transport = ASGITransport(app=app)
    async with AsyncClient(transport=transport, base_url="http://testserver") as ac:
        yield ac
    app.dependency_overrides.clear()


@pytest_asyncio.fixture
async def sample_setup(db_session: AsyncSession):
    """Cria um cenário base com estabelecimento, usuário admin, profissional com grade e serviço."""
    # Estabelecimento
    establishment = Establishment(
        name="Barbearia Vintage",
        slug="barbearia-vintage",
        email="contato@barbearia.com",
        phone="11999998888",
        address="Rua das Flores, 123",
        settings={"slot_interval_minutes": 30},
    )
    db_session.add(establishment)
    await db_session.flush()

    # Usuário Admin
    admin_user = User(
        establishment_id=establishment.id,
        name="Carlos Admin",
        email="admin@barbearia.com",
        password_hash=get_password_hash("senha123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(admin_user)

    # Serviço (Corte de Cabelo - 30 min)
    service = Service(
        establishment_id=establishment.id,
        name="Corte Tradicional",
        description="Corte de cabelo tesoura e máquina",
        duration_minutes=30,
        price=50.00,
        is_active=True,
    )
    db_session.add(service)
    await db_session.flush()

    # Profissional
    professional = Professional(
        establishment_id=establishment.id,
        name="Mestre Barbeiro",
        email="barbeiro@barbearia.com",
        phone="11988887777",
        bio="10 anos de experiência",
        is_active=True,
    )
    db_session.add(professional)
    await db_session.flush()

    # Vínculo Profissional-Serviço
    db_session.add(ProfessionalService(professional_id=professional.id, service_id=service.id))

    # Grade horária semanal (Segunda a Sábado, das 09:00 às 18:00 com almoço 12:00-13:00)
    for day in range(6):  # 0 a 5
        db_session.add(
            ProfessionalWorkingHour(
                professional_id=professional.id,
                day_of_week=day,
                start_time=time(9, 0),
                end_time=time(18, 0),
                break_start_time=time(12, 0),
                break_end_time=time(13, 0),
                is_active=True,
            )
        )

    # Cliente existente
    customer = Customer(
        establishment_id=establishment.id,
        name="João Cliente",
        phone="11977776666",
        email="joao@cliente.com",
    )
    db_session.add(customer)

    await db_session.commit()

    token = create_access_token(subject=str(admin_user.id))

    return {
        "establishment": establishment,
        "admin_user": admin_user,
        "token": token,
        "service": service,
        "professional": professional,
        "customer": customer,
    }
