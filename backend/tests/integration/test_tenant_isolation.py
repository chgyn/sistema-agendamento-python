import pytest
from httpx import AsyncClient
from app.domain.models.establishment import Establishment
from app.domain.models.user import User, UserRole
from app.domain.models.service import Service
from app.core.security import get_password_hash, create_access_token


@pytest.mark.asyncio
async def test_tenant_isolation_on_services_and_access(db_session, client: AsyncClient, sample_setup):
    # Setup do Estabelecimento B
    est_b = Establishment(
        name="Salão Bella Vista",
        slug="salao-bella-vista",
        email="contato@bellavista.com",
        phone="11955554444",
    )
    db_session.add(est_b)
    await db_session.flush()

    user_b = User(
        establishment_id=est_b.id,
        name="Admin Bella",
        email="admin@bellavista.com",
        password_hash=get_password_hash("senha123"),
        role=UserRole.ADMIN,
        is_active=True,
    )
    db_session.add(user_b)

    service_b = Service(
        establishment_id=est_b.id,
        name="Escova Progressiva",
        duration_minutes=90,
        price=180.00,
        is_active=True,
    )
    db_session.add(service_b)
    await db_session.commit()

    token_a = sample_setup["token"]
    headers_a = {"Authorization": f"Bearer {token_a}"}

    # 1. Usuário A lista serviços e NÃO deve enxergar o serviço do Estabelecimento B
    resp_list = await client.get("/api/v1/services", headers=headers_a)
    assert resp_list.status_code == 200
    services_a = resp_list.json()
    service_names = [s["name"] for s in services_a]
    assert "Corte Tradicional" in service_names
    assert "Escova Progressiva" not in service_names

    # 2. Usuário A tenta buscar diretamente pelo ID do serviço do Estabelecimento B
    resp_direct = await client.get(f"/api/v1/services/{service_b.id}", headers=headers_a)
    assert resp_direct.status_code == 404
