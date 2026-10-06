# 💈 Sistema de Agendamento para Barbearias e Salões de Beleza

Monolito modular **Multi-Tenant** de alta performance desenvolvido com **Python 3.12+ (FastAPI + SQLAlchemy 2.0 Async + Celery)** e **Vue 3 (Vite + TypeScript + Tailwind CSS v4)**, orquestrado com **Docker Compose**.

---

## 🚀 Quick Start (Início Rápido)

Com o Docker e Docker Compose instalados, execute:

```bash
# 1. Configurar variáveis de ambiente
cp .env.example .env

# 2. Subir os containers (Postgres 16, Redis 7, FastAPI, Celery, Vue 3)
docker compose up --build -d

# 3. Inserir dados de demonstração (Seed)
docker compose exec backend python scripts/seed.py
```

### 🌐 Acessos Locais:
* **Vitrine Pública (Agendamento do Cliente):** [http://localhost:5173/p/barbearia-retro](http://localhost:5173/p/barbearia-retro)
* **Painel Administrativo:** [http://localhost:5173/login](http://localhost:5173/login)
  * **Admin:** `admin@barbearia.com` / `admin123`
  * **Operador:** `operador@barbearia.com` / `operador123`
* **Swagger API (FastAPI):** [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Stack Tecnológica

### Backend
* **Python 3.12+**
* **FastAPI:** API REST assíncrona de alto desempenho.
* **SQLAlchemy 2.0 (Async com `asyncpg`):** ORM com prevenção ativa de consultas N+1 via `lazy="raise"` e `selectinload`.
* **Alembic:** Gerenciamento de migrações relacionais assíncronas.
* **Pydantic V2:** Validação estrita de contratos de dados e serialização de saída.
* **Celery + Redis:** Fila assíncrona para envio de e-mails, confirmações e notificações.
* **Segurança:** Autenticação JWT, hashing de senhas com Bcrypt (rounds=12) e criptografia de dados sensíveis com AES-256-GCM (`cryptography`).

### Frontend
* **Vue.js 3** com `<script setup>` e Composition API.
* **TypeScript** para tipagem estrita de componentes e stores.
* **Vite 5** como build tool de alta velocidade.
* **Tailwind CSS v4** com tema dark, glassmorphism e micro-animações.
* **Pinia:** Gerenciamento de estado global.
* **Vue Router 4:** Roteamento com guards de autenticação.
* **Lucide Icons:** Ícones modernos e consistentes.

### Infraestrutura & Banco de Dados
* **PostgreSQL 16** (banco de dados relacional com suporte a índices de conflito e JSONB).
* **Redis 7** (broker e backend de resultados para Celery).
* **Docker & Docker Compose** (ambientes isolados em containers com healthchecks).

---

## 📚 Documentação Técnica Completa

A documentação detalhada da arquitetura e contratos está disponível no diretório [`docs/`](file:///home/charles/projetos/test-pythonFast/docs/):

* 🏗️ **[Arquitetura do Sistema](file:///home/charles/projetos/test-pythonFast/docs/ARQUITETURA.md):** Clean Architecture, isolamento multi-tenant e controle de concorrência anti-*double-booking*.
* 📖 **[Catálogo de Endpoints REST](file:///home/charles/projetos/test-pythonFast/docs/API_ENDPOINTS.md):** Especificação completa de todas as rotas FastAPI, parâmetros, respostas e erros HTTP.
* 🚀 **[Guia de Setup e Comandos](file:///home/charles/projetos/test-pythonFast/docs/GUIA_SETUP.md):** Comandos do Docker Compose, migrações Alembic e execução de testes automatizados.
* 🎨 **[Frontend Vue 3 & Pinia](file:///home/charles/projetos/test-pythonFast/docs/FRONTEND_VUE.md):** Arquitetura das telas, wizard público em 4 etapas e stores Pinia.

---

## 🧪 Testes Automatizados

A aplicação conta com testes unitários e de integração assíncronos (`pytest-asyncio` + `httpx.AsyncClient`) executando em **SQLite em memória isolado (`sqlite+aiosqlite:///:memory:`)**, garantindo que nenhum teste afete bancos de dados de desenvolvimento ou produção:

```bash
docker compose exec backend pytest -v
```

**Cenários cobertos:**
1. Prevenção de conflito e reserva concorrente simultânea (*Double-booking* -> HTTP 409).
2. Fluxo público completo de ponta a ponta (Vitrine -> Serviço -> Profissional -> Reserva -> HTTP 201).
3. Isolamento absoluto entre estabelecimentos (Multi-tenant -> HTTP 404 ao tentar acessar recursos de outro tenant).
4. Cálculo inteligente de disponibilidade (descarte de horários passados e intervalos de descanso).
5. Paginação de registros volumosos (`limit` e `offset`).
6. Segurança criptográfica (Bcrypt, JWT e AES-256-GCM).

---

## 📄 Licença
Distribuído sob licença proprietária. Todos os direitos reservados.
