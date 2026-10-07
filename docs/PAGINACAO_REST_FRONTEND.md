# 📖 Documentação Técnica: Paginação Canônica REST & Frontend Vue 3

Esta documentação técnica descreve a arquitetura, endpoints, schemas, parâmetros de requisição e componentes frontend para o módulo de **Paginação Padronizada** do projeto **test-pythonFast**.

---

## 1. 📝 Registro de Alterações (Release Notes)

### Adicionado
- **Schema Canônico Pydantic V2:** [`PaginatedResponse[T]`](file:///home/charles/projetos/test-pythonFast/backend/app/schemas/pagination.py) com campos tipados `items: list[T]`, `total: int`, `page: int`, `page_size: int`, `total_pages: int` e factory `create(...)`.
- **Constantes Globais de Paginação:** `DEFAULT_PAGE_SIZE = 10` e `MAX_PAGE_SIZE = 100` em [`app/schemas/pagination.py`](file:///home/charles/projetos/test-pythonFast/backend/app/schemas/pagination.py).
- **Repositório Base Assíncrono:** Método genérico [`paginate(...)`](file:///home/charles/projetos/test-pythonFast/backend/app/repositories/base.py) no SQLAlchemy 2.0 com subquery de contagem sem sort overhead (`order_by(None)`).
- **Consultas Paginadas nos Repositórios:**
  - `CustomerRepository.list_by_establishment_paginated` com busca textual case-insensitive.
  - `ServiceRepository.list_by_establishment_paginated` com filtro de serviços ativos e busca por nome.
  - `ProfessionalRepository.list_by_establishment_paginated` com `selectinload`, filtro por serviço e busca.
  - `AppointmentRepository.list_by_period_paginated` com intervalo de datas, status e ordenação cronológica.
- **Componente Reutilizável de Paginação:** [`Pagination.vue`](file:///home/charles/projetos/test-pythonFast/frontend/src/components/ui/Pagination.vue) com layout Tailwind CSS v4 Dark Glassmorphism, seletor de itens por página (10, 20, 50) e navegação numérica com ellipsis dinâmico.
- **Testes de Integração:** Bateria de testes assíncronos em [`tests/integration/test_pagination.py`](file:///home/charles/projetos/test-pythonFast/backend/tests/integration/test_pagination.py) cobrindo envelope canônico, disjunção de registros e busca sem resultados (`total: 0`, `total_pages: 0`).

### Modificado
- Endpoints de listagem convertidos de `list[T]` plano para `PaginatedResponse[T]`:
  - `GET /api/v1/customers`
  - `GET /api/v1/services`
  - `GET /api/v1/professionals`
  - `GET /api/v1/appointments`
- Store Pinia [`appointments.ts`](file:///home/charles/projetos/test-pythonFast/frontend/src/stores/appointments.ts) atualizada com gerenciamento reativo do estado de paginação.
- Telas administrativas ([CustomersView.vue](file:///home/charles/projetos/test-pythonFast/frontend/src/pages/admin/CustomersView.vue), [ServicesView.vue](file:///home/charles/projetos/test-pythonFast/frontend/src/pages/admin/ServicesView.vue), [ProfessionalsView.vue](file:///home/charles/projetos/test-pythonFast/frontend/src/pages/admin/ProfessionalsView.vue), [AppointmentsListView.vue](file:///home/charles/projetos/test-pythonFast/frontend/src/pages/admin/AppointmentsListView.vue)) integradas ao componente `Pagination.vue`.

---

## 2. 🚀 Guia de Setup & Execução

### Execução via Docker Compose (Recomendado)
```bash
# Subir containers em segundo plano
docker compose up -d

# Executar testes da suíte completa do backend
docker exec appointment_backend pytest -v

# Validar typecheck e build de produção do frontend
docker exec appointment_frontend npm run build
```

### Execução Local sem Docker
```bash
# 1. Backend FastAPI
cd backend
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt  # ou poetry install
uvicorn app.main:app --reload --host 0.0.0.0 --port 8000

# 2. Worker Celery
celery -A app.workers.celery_app worker --loglevel=info

# 3. Frontend Vue 3
cd ../frontend
npm install
npm run dev
```

---

## 3. 📖 Especificação da API REST (Endpoints Paginados)

### 3.1. Envelope Padronizado JSON

Todas as listagens administrativas retornam o seguinte contrato uniforme:

```json
{
  "items": [
    { ... }
  ],
  "total": 45,
  "page": 1,
  "page_size": 10,
  "total_pages": 5
}
```

> **Semântica:** Quando nenhum registro for encontrado para os filtros informados, a resposta retorna `"items": []`, `"total": 0` e `"total_pages": 0`.

### 3.2. Parâmetros de Query Padronizados

| Parâmetro | Tipo | Padrão | Validação | Descrição |
| :--- | :--- | :---: | :---: | :--- |
| `page` | `integer` | `1` | `ge=1` | Número da página solicitada (índice baseado em 1). |
| `page_size` | `integer` | `10` | `ge=1, le=100` | Quantidade de registros por página (máx. 100). |
| `search` | `string` | `null` | Opcional | Termo de busca textual (nome, telefone). |
| `all_records` | `boolean` | `false` | Opcional | *(Disponível em serviços/profissionais)* Retorna catálogo completo até 100 itens para preenchimento de dropdowns. |

### 3.3. Tabela de Endpoints

| Método | Endpoint URI | Permissão | Resposta | Descrição |
| :--- | :--- | :--- | :--- | :--- |
| `GET` | `/api/v1/customers` | `Bearer JWT` | `PaginatedResponse[CustomerResponse]` | Lista clientes com paginação e busca por nome ou celular. |
| `GET` | `/api/v1/services` | `Bearer JWT` | `PaginatedResponse[ServiceResponse]` | Lista serviços do catálogo com `active_only`, busca e paginação. |
| `GET` | `/api/v1/professionals` | `Bearer JWT` | `PaginatedResponse[ProfessionalResponse]` | Lista profissionais com `service_id`, `active_only` e paginação. |
| `GET` | `/api/v1/appointments` | `Bearer JWT` | `PaginatedResponse[AppointmentDetailResponse]` | Lista agendamentos filtrados por intervalo de datas e status. |

### 3.4. Exemplo de Requisição e Resposta

#### Exemplo: Listagem de Clientes com Busca
```bash
curl -X GET "http://localhost:8000/api/v1/customers?page=1&page_size=10&search=Silva" \
  -H "Authorization: Bearer <SEU_TOKEN_JWT>"
```

**Resposta HTTP 200 OK:**
```json
{
  "items": [
    {
      "id": "1e860950-8b4b-4835-9774-706f3e588d36",
      "establishment_id": "9b1deb4d-3b7d-4bad-9bdd-2b0d7b3dcb6d",
      "name": "Maria Silva",
      "phone": "11988889999",
      "email": "maria@exemplo.com",
      "created_at": "2026-10-06T15:30:00Z"
    }
  ],
  "total": 1,
  "page": 1,
  "page_size": 10,
  "total_pages": 1
}
```

#### Respostas de Erro Comuns
- `401 Unauthorized`: Token JWT ausente, expirado ou inválido.
- `422 Unprocessable Entity`: Parâmetro fora do intervalo (ex: `page_size > 100` ou `page < 1`).

---

## 4. 🔄 Tarefas Assíncronas & Workers (Celery)

As consultas paginadas são de leitura imediata e executam assincronamente através do pool do SQLAlchemy (`asyncpg`) no event loop principal do FastAPI.

O worker Celery permanece responsável pelas tarefas transacionais de background associadas aos agendamentos:
- **`app.workers.tasks.send_appointment_confirmation`**: Disparo assíncrono de e-mail/notificação após confirmação de reserva.
- **`app.workers.tasks.send_appointment_cancellation`**: Notificação assíncrona com justificativa de cancelamento.

---

## 5. 💡 Componentes Frontend & Consumo com Axios

### 5.1. Componente Reutilizável `Pagination.vue`

Localizado em [`frontend/src/components/ui/Pagination.vue`](file:///home/charles/projetos/test-pythonFast/frontend/src/components/ui/Pagination.vue).

#### Props
```typescript
interface Props {
  page: number;              // Página atual (1-based)
  pageSize: number;          // Tamanho da página
  total: number;             // Quantidade total de registros
  totalPages: number;        // Quantidade total de páginas
  isLoading?: boolean;       // Bloqueia interações durante requisições
  pageSizeOptions?: number[];// Opções do dropdown (padrão: [10, 20, 50])
}
```

#### Emits
- `@update:page(newPage: number)`
- `@update:pageSize(newPageSize: number)`
- `@change({ page, pageSize }: { page: number, pageSize: number })`

#### Exemplo de Uso no Template Vue 3
```vue
<script setup lang="ts">
import { ref, onMounted } from 'vue';
import Pagination from '@/components/ui/Pagination.vue';
import api from '@/services/api';

const items = ref([]);
const isLoading = ref(false);
const pagination = ref({ page: 1, pageSize: 10, total: 0, totalPages: 0 });

async function loadData(page = 1, pageSize = 10) {
  isLoading.value = true;
  try {
    const res = await api.get('/customers', { params: { page, page_size: pageSize } });
    items.value = res.data.items;
    pagination.value = {
      page: res.data.page,
      pageSize: res.data.page_size,
      total: res.data.total,
      totalPages: res.data.total_pages,
    };
  } finally {
    isLoading.value = false;
  }
}

onMounted(() => loadData());
</script>

<template>
  <div>
    <!-- Sua tabela / lista de dados -->
    <Pagination
      :page="pagination.page"
      :page-size="pagination.pageSize"
      :total="pagination.total"
      :total-pages="pagination.totalPages"
      :is-loading="isLoading"
      @change="({ page, pageSize }) => loadData(page, pageSize)"
    />
  </div>
</template>
```

---

## 6. 🧪 Estratégia de Testes Automatizados

Os testes do backend cobrem:
1. **Contrato Canônico:** Validação de formato das chaves `items`, `total`, `page`, `page_size` e `total_pages`.
2. **Disjunção de Páginas:** Garantia de que a página 1 e página 2 não repetem identificadores de entidades.
3. **Cálculo de Teto:** Confirmação de que `total_pages == ceil(total / page_size)`.
4. **Busca sem Registros:** Retorno de `total: 0`, `total_pages: 0` e lista de itens vazia.
5. **Isolamento de Tenants:** Prova de que a contagem e os itens pertencem única e exclusivamente ao `establishment_id` autenticado.
