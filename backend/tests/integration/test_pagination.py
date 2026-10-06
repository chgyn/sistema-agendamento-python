from datetime import datetime, time, date, timedelta, timezone
import pytest
from httpx import AsyncClient
from app.domain.models.customer import Customer
from app.domain.models.appointment import Appointment, AppointmentStatus


@pytest.mark.asyncio
async def test_customers_and_appointments_pagination(db_session, client: AsyncClient, sample_setup):
    establishment = sample_setup["establishment"]
    token = sample_setup["token"]
    headers = {"Authorization": f"Bearer {token}"}
    service = sample_setup["service"]
    professional = sample_setup["professional"]

    # Cria 5 clientes adicionais no estabelecimento
    customers = []
    for i in range(5):
        c = Customer(
            establishment_id=establishment.id,
            name=f"Cliente Paginado {i}",
            phone=f"1190000000{i}",
            email=f"cliente{i}@teste.com",
        )
        db_session.add(c)
        customers.append(c)

    await db_session.commit()

    # 1. Testa paginação com limit=2, offset=0
    resp_page_1 = await client.get("/api/v1/customers?limit=2&offset=0", headers=headers)
    assert resp_page_1.status_code == 200
    data_page_1 = resp_page_1.json()
    assert len(data_page_1) == 2

    # 2. Testa paginação com limit=2, offset=2
    resp_page_2 = await client.get("/api/v1/customers?limit=2&offset=2", headers=headers)
    assert resp_page_2.status_code == 200
    data_page_2 = resp_page_2.json()
    assert len(data_page_2) == 2

    # Os registros da página 1 e página 2 não devem se repetir
    ids_page_1 = {c["id"] for c in data_page_1}
    ids_page_2 = {c["id"] for c in data_page_2}
    assert ids_page_1.isdisjoint(ids_page_2)
