from datetime import date, datetime, time, timedelta, timezone
import pytest
from httpx import AsyncClient


@pytest.mark.asyncio
async def test_appointment_double_booking_conflict_prevention(client: AsyncClient, sample_setup):
    establishment = sample_setup["establishment"]
    service = sample_setup["service"]
    professional = sample_setup["professional"]

    future_date = date.today() + timedelta(days=2)
    start_dt = datetime.combine(future_date, time(14, 0)).replace(tzinfo=timezone.utc)

    payload_1 = {
        "service_id": str(service.id),
        "professional_id": str(professional.id),
        "start_datetime": start_dt.isoformat(),
        "customer_name": "Cliente Um",
        "customer_phone": "11911111111",
    }

    payload_2 = {
        "service_id": str(service.id),
        "professional_id": str(professional.id),
        "start_datetime": start_dt.isoformat(),
        "customer_name": "Cliente Dois",
        "customer_phone": "11922222222",
    }

    # Primeira requisição: Deve ter sucesso
    resp1 = await client.post(
        f"/api/v1/public/{establishment.slug}/appointments",
        json=payload_1,
    )
    assert resp1.status_code == 201

    # Segunda requisição para exatamente o mesmo slot: Deve ser rejeitada com 409 Conflict
    resp2 = await client.post(
        f"/api/v1/public/{establishment.slug}/appointments",
        json=payload_2,
    )
    assert resp2.status_code == 409
    data2 = resp2.json()
    assert "não está mais disponível" in data2["message"] or "acabou de ser reservado" in data2["message"]
