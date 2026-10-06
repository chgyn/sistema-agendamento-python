import math
import pytest
from httpx import AsyncClient
from app.domain.models.customer import Customer
from app.domain.models.service import Service


@pytest.mark.asyncio
async def test_canonical_pagination_customers_and_services(db_session, client: AsyncClient, sample_setup):
    establishment = sample_setup["establishment"]
    token = sample_setup["token"]
    headers = {"Authorization": f"Bearer {token}"}

    # 1. Cria 6 clientes adicionais no estabelecimento
    for i in range(6):
        c = Customer(
            establishment_id=establishment.id,
            name=f"Cliente Paginado {i:02d}",
            phone=f"119000000{i:02d}",
            email=f"cliente{i}@teste.com",
        )
        db_session.add(c)

    # 2. Cria 4 serviços adicionais
    for i in range(4):
        s = Service(
            establishment_id=establishment.id,
            name=f"Serviço Extra {i}",
            description="Descrição do serviço",
            duration_minutes=30,
            price=45.0,
            is_active=True,
        )
        db_session.add(s)

    await db_session.commit()

    # --- Teste de Clientes ---
    # Página 1 com page_size=3
    resp_page_1 = await client.get("/api/v1/customers?page=1&page_size=3", headers=headers)
    assert resp_page_1.status_code == 200
    data_page_1 = resp_page_1.json()

    assert "items" in data_page_1
    assert "total" in data_page_1
    assert "page" in data_page_1
    assert "page_size" in data_page_1
    assert "total_pages" in data_page_1

    assert data_page_1["page"] == 1
    assert data_page_1["page_size"] == 3
    assert len(data_page_1["items"]) == 3
    total_customers = data_page_1["total"]
    assert total_customers >= 6
    assert data_page_1["total_pages"] == math.ceil(total_customers / 3)

    # Página 2 com page_size=3
    resp_page_2 = await client.get("/api/v1/customers?page=2&page_size=3", headers=headers)
    assert resp_page_2.status_code == 200
    data_page_2 = resp_page_2.json()
    assert data_page_2["page"] == 2
    assert len(data_page_2["items"]) == 3

    # Garantir que os itens da página 1 e página 2 são disjuntos
    ids_page_1 = {c["id"] for c in data_page_1["items"]}
    ids_page_2 = {c["id"] for c in data_page_2["items"]}
    assert ids_page_1.isdisjoint(ids_page_2)

    # --- Teste de Serviços ---
    resp_services = await client.get("/api/v1/services?page=1&page_size=2", headers=headers)
    assert resp_services.status_code == 200
    services_data = resp_services.json()
    assert "items" in services_data
    assert "total" in services_data
    assert services_data["page"] == 1
    assert services_data["page_size"] == 2
    assert len(services_data["items"]) == 2
    assert services_data["total"] >= 5

    # --- Teste de Profissionais ---
    resp_profs = await client.get("/api/v1/professionals?page=1&page_size=10", headers=headers)
    assert resp_profs.status_code == 200
    profs_data = resp_profs.json()
    assert "items" in profs_data
    assert "total" in profs_data
    assert profs_data["page"] == 1
    assert len(profs_data["items"]) >= 1

    # --- Teste de Agendamentos ---
    resp_appts = await client.get("/api/v1/appointments?page=1&page_size=10", headers=headers)
    assert resp_appts.status_code == 200
    appts_data = resp_appts.json()
    assert "items" in appts_data
    assert "total" in appts_data
    assert appts_data["page"] == 1

    # --- Teste de Busca sem resultados (total=0, total_pages=0) ---
    resp_empty = await client.get("/api/v1/customers?search=NomeInexistenteXYZ123", headers=headers)
    assert resp_empty.status_code == 200
    empty_data = resp_empty.json()
    assert empty_data["total"] == 0
    assert empty_data["total_pages"] == 0
    assert empty_data["items"] == []
