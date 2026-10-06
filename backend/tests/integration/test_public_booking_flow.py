from datetime import date, datetime, time, timedelta, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_full_public_booking_flow(client: AsyncClient, sample_setup):
    establishment = sample_setup["establishment"]
    service = sample_setup["service"]
    professional = sample_setup["professional"]

    # 1. Consulta dados públicos do estabelecimento
    resp = await client.get(f"/api/v1/public/{establishment.slug}")
    assert resp.status_code == 200
    data = resp.json()
    assert data["name"] == establishment.name

    # 2. Consulta serviços
    resp_services = await client.get(f"/api/v1/public/{establishment.slug}/services")
    assert resp_services.status_code == 200
    assert len(resp_services.json()) >= 1

    # 3. Consulta profissionais
    resp_profs = await client.get(
        f"/api/v1/public/{establishment.slug}/professionals?service_id={service.id}"
    )
    assert resp_profs.status_code == 200
    assert len(resp_profs.json()) >= 1

    # 4. Agendamento para uma data futura
    future_date = date.today() + timedelta(days=3)
    start_dt = datetime.combine(future_date, time(10, 0)).replace(tzinfo=timezone.utc)

    payload = {
        "service_id": str(service.id),
        "professional_id": str(professional.id),
        "start_datetime": start_dt.isoformat(),
        "customer_name": "Maria Silva",
        "customer_phone": "11988889999",
        "customer_email": "maria@exemplo.com",
        "notes": "Primeiro atendimento",
    }

    resp_booking = await client.post(
        f"/api/v1/public/{establishment.slug}/appointments",
        json=payload,
    )
    assert resp_booking.status_code == 201
    booking_data = resp_booking.json()
    assert booking_data["status"] == "SCHEDULED"
    assert booking_data["service_name"] == service.name
    assert booking_data["professional_name"] == professional.name
