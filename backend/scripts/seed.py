import asyncio
import sys
import os

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))
from datetime import datetime, date, time, timedelta, timezone
from decimal import Decimal
from sqlalchemy import select
from app.core.database import AsyncSessionLocal
from app.core.security import get_password_hash
from app.domain.models import (
    Establishment,
    User,
    UserRole,
    Service,
    Professional,
    ProfessionalService,
    ProfessionalWorkingHour,
    Customer,
    Appointment,
    AppointmentStatus,
)


async def seed():
    async with AsyncSessionLocal() as session:
        # Verifica se já existe o estabelecimento
        stmt = select(Establishment).where(Establishment.slug == "barbearia-retro")
        existing = (await session.execute(stmt)).scalar_one_or_none()
        if existing:
            print("ℹ️ Dados de seed já foram inseridos previamente.")
            return

        print("🌱 Populando banco com dados de demonstração...")

        # 1. Estabelecimento
        establishment = Establishment(
            name="Barbearia Retrô Club",
            slug="barbearia-retro",
            email="contato@barbeariaretro.com.br",
            phone="(11) 99999-8888",
            address="Av. Paulista, 1000 - Bela Vista, São Paulo - SP",
            settings={"slot_interval_minutes": 30},
        )
        session.add(establishment)
        await session.flush()

        # 2. Usuários
        admin_user = User(
            establishment_id=establishment.id,
            name="Carlos Admin",
            email="admin@barbearia.com",
            password_hash=get_password_hash("admin123"),
            role=UserRole.ADMIN,
            is_active=True,
        )
        operator_user = User(
            establishment_id=establishment.id,
            name="Mariana Recepção",
            email="operador@barbearia.com",
            password_hash=get_password_hash("operador123"),
            role=UserRole.OPERATOR,
            is_active=True,
        )
        session.add_all([admin_user, operator_user])

        # 3. Serviços
        s1 = Service(
            establishment_id=establishment.id,
            name="Corte Clássico & Fade",
            description="Corte tradicional com degradê navalhado, lavagem e finalização premium.",
            duration_minutes=45,
            price=Decimal("60.00"),
            is_active=True,
        )
        s2 = Service(
            establishment_id=establishment.id,
            name="Barba Terapia & Toalha Quente",
            description="Design de barba com esfoliação, toalha quente e óleos essenciais.",
            duration_minutes=35,
            price=Decimal("45.00"),
            is_active=True,
        )
        s3 = Service(
            establishment_id=establishment.id,
            name="Combo VIP: Corte + Barba",
            description="Experiência completa de cuidado capilar e barboterapia.",
            duration_minutes=75,
            price=Decimal("95.00"),
            is_active=True,
        )
        session.add_all([s1, s2, s3])
        await session.flush()

        # 4. Profissionais
        p1 = Professional(
            establishment_id=establishment.id,
            name="Bruno 'Navalha' Santos",
            email="bruno@barbeariaretro.com.br",
            phone="(11) 98888-1111",
            bio="Especialista em visagismo e cortes clássicos há mais de 8 anos.",
            is_active=True,
        )
        p2 = Professional(
            establishment_id=establishment.id,
            name="Felipe Barbeiro",
            email="felipe@barbeariaretro.com.br",
            phone="(11) 98888-2222",
            bio="Especialista em barba lenhador e designs modernos.",
            is_active=True,
        )
        session.add_all([p1, p2])
        await session.flush()

        # Vincula serviços aos profissionais
        for s in [s1, s2, s3]:
            session.add(ProfessionalService(professional_id=p1.id, service_id=s.id))
            session.add(ProfessionalService(professional_id=p2.id, service_id=s.id))

        # Grade horária semanal (Segunda a Sábado das 09:00 às 19:00, almoço 12:30-13:30)
        for day in range(6):
            session.add(
                ProfessionalWorkingHour(
                    professional_id=p1.id,
                    day_of_week=day,
                    start_time=time(9, 0),
                    end_time=time(19, 0),
                    break_start_time=time(12, 30),
                    break_end_time=time(13, 30),
                    is_active=True,
                )
            )
            session.add(
                ProfessionalWorkingHour(
                    professional_id=p2.id,
                    day_of_week=day,
                    start_time=time(10, 0),
                    end_time=time(20, 0),
                    break_start_time=time(13, 0),
                    break_end_time=time(14, 0),
                    is_active=True,
                )
            )

        # 5. Clientes
        c1 = Customer(
            establishment_id=establishment.id,
            name="Rafael Souza",
            phone="(11) 97777-1234",
            email="rafael@cliente.com",
        )
        c2 = Customer(
            establishment_id=establishment.id,
            name="Lucas Ferreira",
            phone="(11) 97777-5678",
            email="lucas@cliente.com",
        )
        session.add_all([c1, c2])
        await session.flush()

        # 6. Agendamentos de Demonstração para Hoje
        today = date.today()
        appt1 = Appointment(
            establishment_id=establishment.id,
            customer_id=c1.id,
            professional_id=p1.id,
            service_id=s1.id,
            start_datetime=datetime.combine(today, time(10, 0)).replace(tzinfo=timezone.utc),
            end_datetime=datetime.combine(today, time(10, 45)).replace(tzinfo=timezone.utc),
            status=AppointmentStatus.CONFIRMED,
            notes="Cliente prefere degradê baixo.",
        )
        appt2 = Appointment(
            establishment_id=establishment.id,
            customer_id=c2.id,
            professional_id=p2.id,
            service_id=s2.id,
            start_datetime=datetime.combine(today, time(11, 0)).replace(tzinfo=timezone.utc),
            end_datetime=datetime.combine(today, time(11, 35)).replace(tzinfo=timezone.utc),
            status=AppointmentStatus.SCHEDULED,
        )
        session.add_all([appt1, appt2])

        await session.commit()
        print("✅ Dados de seed criados com sucesso!")
        print("\n🔑 Credenciais de Acesso:")
        print("   Administrador: admin@barbearia.com / admin123")
        print("   Operador:      operador@barbearia.com / operador123")
        print("   Página Pública: http://localhost:5173/p/barbearia-retro\n")


if __name__ == "__main__":
    asyncio.run(seed())
