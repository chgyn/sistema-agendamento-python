# 📖 Catálogo de Endpoints REST (FastAPI)

A API segue os padrões RESTful, com prefixo base `/api/v1` e documentação interativa OpenAPI disponível em `/docs` (Swagger UI) e `/redoc` (ReDoc).

---

## 1. Tabela Geral de Rotas

| Método | Endpoint URI | Tag | Autenticação / Permissão | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| **POST** | `/api/v1/auth/login` | Autenticação | Aberto | Realiza login e retorna JWT Bearer Token. |
| **GET** | `/api/v1/auth/me` | Autenticação | `Bearer JWT` | Retorna os dados do usuário autenticado e tenant. |
| **GET** | `/api/v1/public/{slug}` | Público | Aberto | Consulta informações públicas do estabelecimento. |
| **GET** | `/api/v1/public/{slug}/services` | Público | Aberto | Lista os serviços ativos do estabelecimento. |
| **GET** | `/api/v1/public/{slug}/professionals` | Público | Aberto | Lista os profissionais que realizam um serviço. |
| **GET** | `/api/v1/public/{slug}/availability` | Público | Aberto | Calcula slots livres para data, serviço e profissional. |
| **POST** | `/api/v1/public/{slug}/appointments` | Público | Aberto | Confirma reserva pública pelo cliente (anti-conflito). |
| **POST** | `/api/v1/establishment/register` | Estabelecimento | Aberto | Cria nova conta de estabelecimento e primeiro admin. |
| **GET** | `/api/v1/establishment/me` | Estabelecimento | `Bearer JWT` | Retorna configurações do estabelecimento atual. |
| **PATCH**| `/api/v1/establishment/me` | Estabelecimento | `Bearer JWT (ADMIN)` | Atualiza dados cadastrais do estabelecimento. |
| **GET** | `/api/v1/services` | Serviços | `Bearer JWT` | Lista todos os serviços do estabelecimento. |
| **POST** | `/api/v1/services` | Serviços | `Bearer JWT (ADMIN)` | Cadastra um novo serviço com duração e preço. |
| **GET** | `/api/v1/services/{id}` | Serviços | `Bearer JWT` | Obtém detalhes de um serviço específico. |
| **PUT** | `/api/v1/services/{id}` | Serviços | `Bearer JWT (ADMIN)` | Atualiza dados e valores de um serviço. |
| **GET** | `/api/v1/professionals` | Profissionais | `Bearer JWT` | Lista profissionais e vínculos do estabelecimento. |
| **POST** | `/api/v1/professionals` | Profissionais | `Bearer JWT (ADMIN)` | Cadastra profissional e associa serviços. |
| **GET** | `/api/v1/professionals/{id}` | Profissionais | `Bearer JWT` | Obtém detalhes completos do profissional. |
| **PUT** | `/api/v1/professionals/{id}` | Profissionais | `Bearer JWT (ADMIN)` | Atualiza dados cadastrais do profissional. |
| **PUT** | `/api/v1/professionals/{id}/working-hours` | Profissionais | `Bearer JWT (ADMIN)` | Configura grade semanal de expediente e almoço. |
| **POST** | `/api/v1/professionals/{id}/unavailabilities` | Profissionais | `Bearer JWT` | Registra bloqueio pontual na agenda do profissional. |
| **GET** | `/api/v1/appointments` | Agendamentos | `Bearer JWT` | Lista agendamentos filtrados por período, status e prof. |
| **POST** | `/api/v1/appointments` | Agendamentos | `Bearer JWT` | Cria agendamento manual interno pelo operador. |
| **PATCH**| `/api/v1/appointments/{id}/status` | Agendamentos | `Bearer JWT` | Altera status (`CONFIRMED`, `COMPLETED`, `NO_SHOW`). |
| **POST** | `/api/v1/appointments/{id}/cancel` | Agendamentos | `Bearer JWT` | Cancela agendamento mantendo histórico e justificativa. |
| **GET** | `/api/v1/customers` | Clientes | `Bearer JWT` | Lista clientes atendidos pelo estabelecimento (paginado). |
| **GET** | `/api/v1/customers/{id}` | Clientes | `Bearer JWT` | Consulta dados de um cliente específico. |

---

## 2. Exemplos de Requisições e Respostas

### 2.1 Autenticação (`POST /api/v1/auth/login`)
**Requisição:**
```bash
curl -X POST http://localhost:8000/api/v1/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "admin@barbearia.com",
    "password": "admin123"
  }'
```
**Resposta (HTTP 200 OK):**
```json
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 86400
}
```

---

### 2.2 Consulta de Disponibilidade (`GET /api/v1/public/{slug}/availability`)
**Query Parameters:**
- `professional_id` (UUID): ID do profissional escolhido.
- `service_id` (UUID): ID do serviço escolhido.
- `date` (YYYY-MM-DD): Data do atendimento.

**Resposta (HTTP 200 OK):**
```json
{
  "date": "2026-10-07",
  "professional_id": "b93846d3-9e61-4b05-b18a-6899e664b3ef",
  "service_id": "c03baf9a-2943-43b6-9d16-099d379aca74",
  "slots": [
    { "start_time": "09:00", "end_time": "09:45", "is_available": true },
    { "start_time": "09:45", "end_time": "10:30", "is_available": true },
    { "start_time": "12:30", "end_time": "13:15", "is_available": false }
  ]
}
```

---

### 2.3 Realizar Agendamento Público (`POST /api/v1/public/{slug}/appointments`)
**Requisição:**
```bash
curl -X POST http://localhost:8000/api/v1/public/barbearia-retro/appointments \
  -H "Content-Type: application/json" \
  -d '{
    "service_id": "c03baf9a-2943-43b6-9d16-099d379aca74",
    "professional_id": "b93846d3-9e61-4b05-b18a-6899e664b3ef",
    "start_datetime": "2026-10-07T14:00:00Z",
    "customer_name": "Marcos Oliveira",
    "customer_phone": "(11) 98123-4567",
    "customer_email": "marcos@exemplo.com",
    "notes": "Cliente novo"
  }'
```
**Resposta (HTTP 201 Created):**
```json
{
  "id": "e4b2d56a-1290-482a-bc3e-09123847a112",
  "start_datetime": "2026-10-07T14:00:00Z",
  "end_datetime": "2026-10-07T14:45:00Z",
  "status": "SCHEDULED",
  "service_name": "Corte Clássico & Fade",
  "professional_name": "Bruno 'Navalha' Santos",
  "message": "Agendamento realizado com sucesso!"
}
```

**Resposta em caso de Conflito de Horário Simultâneo (HTTP 409 Conflict):**
```json
{
  "error": true,
  "message": "Este horário acabou de ser reservado. Por favor, selecione outro.",
  "details": null,
  "type": "AppointmentConflictError"
}
```

---

### 2.4 Listagem Paginada de Agendamentos (`GET /api/v1/appointments`)
**Query Parameters:**
- `start_date` (ISO 8601, opcional): Data inicial do filtro.
- `end_date` (ISO 8601, opcional): Data final do filtro.
- `professional_id` (UUID, opcional): Filtro por profissional.
- `status` (opcional): Filtro por status (`SCHEDULED`, `CONFIRMED`, `COMPLETED`, `CANCELLED`, `NO_SHOW`).
- `page` (int, default=1, min=1): Número da página.
- `page_size` (int, default=10, min=1, max=100): Quantidade de itens por página.

**Resposta (HTTP 200 OK):**
```json
{
  "items": [
    {
      "id": "e4b2d56a-1290-482a-bc3e-09123847a112",
      "establishment_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "customer_id": "1e860950-8b4b-4835-9774-706f3e588d36",
      "customer_name": "Carlos Lima",
      "customer_phone": "11977778888",
      "professional_id": "4a123f89-8d76-4e55-9012-3456789abcde",
      "professional_name": "Bruno Santos",
      "service_id": "7b891234-5678-90ab-cdef-1234567890ab",
      "service_name": "Corte Clássico",
      "start_datetime": "2026-10-07T14:00:00Z",
      "end_datetime": "2026-10-07T14:45:00Z",
      "status": "CONFIRMED",
      "notes": "Cliente novo"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

---

### 2.5 Padrão Canônico de Paginação (`PaginatedResponse[T]`)

Todas as listagens administrativas (`/customers`, `/services`, `/professionals`, `/appointments`) obedecem ao contrato padronizado:
- `page`: Número da página (1-based, default `1`).
- `page_size`: Quantidade por página (default `10`, max `100`).
- Retorno:
  - `items`: Lista dos registros da página.
  - `total`: Quantidade total de registros encontrados.
  - `page`: Página atual.
  - `page_size`: Tamanho de cada página.
  - `total_pages`: Total de páginas (`ceil(total / page_size)` ou `0` se não houver registros).
