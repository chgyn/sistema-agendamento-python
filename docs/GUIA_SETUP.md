# 🚀 Guia de Setup, Execução & Comandos

## 1. Pré-Requisitos
- Docker (versão 24+) e Docker Compose (v2+)
- (Opcional para desenvolvimento sem Docker): Python 3.12+ e Node.js 20+

---

## 2. Inicialização Rápida com Docker Compose

Clone o repositório e inicie os containers em segundo plano:
```bash
# 1. Configurar variáveis de ambiente
cp .env.example .env

# 2. Construir e subir os containers (PostgreSQL, Redis, Backend, Celery, Frontend)
docker compose up --build -d

# 3. Popular o banco com dados de demonstração (Seed)
docker compose exec backend python scripts/seed.py
```

### Serviços Disponíveis:
- **Frontend (Vue 3 / Vite):** [http://localhost:5173](http://localhost:5173)
  - Vitrine Pública de Demonstração: [http://localhost:5173/p/barbearia-retro](http://localhost:5173/p/barbearia-retro)
  - Login Administrativo: [http://localhost:5173/login](http://localhost:5173/login)
- **Backend (FastAPI REST API):** [http://localhost:8000](http://localhost:8000)
  - Documentação Swagger OpenAPI: [http://localhost:8000/docs](http://localhost:8000/docs)
  - Documentação ReDoc: [http://localhost:8000/redoc](http://localhost:8000/redoc)
- **PostgreSQL 16:** `localhost:5432` (`database: appointment_db`, `user: postgres`, `pass: postgres`)
- **Redis 7:** `localhost:6379`

---

## 3. Gestão de Migrações do Banco (Alembic)

O container `backend` já está configurado no `docker-compose.yml` para executar `alembic upgrade head` automaticamente antes de iniciar o Uvicorn.

### Comandos Manuais do Alembic:
```bash
# Aplicar todas as migrações pendentes no PostgreSQL
docker compose exec backend alembic upgrade head

# Criar nova migração após alterar modelos SQLAlchemy
docker compose exec backend alembic revision --autogenerate -m "adiciona_nova_coluna"

# Desfazer a última migração aplicada (Rollback)
docker compose exec backend alembic downgrade -1

# Verificar a versão atual aplicada no banco
docker compose exec backend alembic current
```

---

## 4. Execução dos Testes Automatizados

Seguindo a regra de isolamento absoluto de banco de dados, os testes rodam contra **SQLite assíncrono em memória** (`sqlite+aiosqlite:///:memory:`):

```bash
# Executar toda a suíte de testes do backend
docker compose exec backend pytest -v

# Executar apenas testes de integração
docker compose exec backend pytest tests/integration/ -v

# Executar testes unitários
docker compose exec backend pytest tests/unit/ -v
```

---

## 5. Variáveis de Ambiente (`.env`)

| Variável | Padrão | Descrição |
| :--- | :--- | :--- |
| `ENVIRONMENT` | `development` | Ambiente da aplicação (`development`, `staging`, `production`). |
| `DEBUG` | `true` | Ativa logs detalhados e documentação Swagger. |
| `DATABASE_URL` | `postgresql+asyncpg://...` | URI assíncrona do PostgreSQL com driver `asyncpg`. |
| `SECRET_KEY` | *(string aleatória)* | Segredo para assinatura de tokens JWT. |
| `AES_ENCRYPTION_KEY`| *(base64 32 bytes)* | Chave simétrica para criptografia AES-256-GCM. |
| `REDIS_URL` | `redis://redis:6379/0` | URL de conexão com a instância do Redis. |
| `CELERY_BROKER_URL`| `redis://redis:6379/0` | Broker de mensagens para tarefas do Celery. |
| `BACKEND_CORS_ORIGINS`| `http://localhost:5173,...`| Domínios autorizados para requisições cross-origin. |
| `VITE_API_BASE_URL` | `http://localhost:8000` | URL base consumida pelo frontend Axios. |
