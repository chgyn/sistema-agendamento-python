---
name: fastapi-architecture
description: Diretrizes de arquitetura Clean/Hexagonal, boas práticas Python 3.12+, FastAPI, SQLAlchemy 2.0 Async, Pydantic V2, Celery (Redis), concorrência assíncrona, criptografia AES-256-GCM e Vue 3 para o projeto test-pythonFast.
---

# 📐 Skill: Python (FastAPI) Clean Architecture & Best Practices Standard

Você é um especialista em engenharia de software com foco no ecossistema Python (3.12+), Clean Architecture, FastAPI, SQLAlchemy 2.0 Async, Pydantic V2, Celery (Redis), PostgreSQL e Vue 3. Siga estritamente estas diretrizes ao planejar, revisar ou implementar código neste projeto.

---

## 1. Princípios de Python Moderno (Python 3.12+)

- **Tipagem Estrita e Type Hints Modernos:**
  - Utilize a sintaxe moderna de tipos da PEP 585 e PEP 604: prefira `str | None` a `Optional[str]`, `list[User]` a `List[User]`, e `dict[str, Any]` a `Dict[str, Any]`.
  - Utilize `Annotated[...]` para injeção de dependências no FastAPI (ex: `CurrentSession = Annotated[AsyncSession, Depends(get_db)]`).
- **Assincronismo Seguro & Integridade do Event Loop:**
  - Todas as funções de rota e operações I/O devem ser assíncronas (`async def`).
  - **NUNCA bloqueie o Event Loop do asyncio:**
    - ❌ Proibido: `time.sleep()`, chamadas síncronas com a lib `requests`, queries síncronas do SQLAlchemy ou leitura bloqueante de arquivos pesados dentro de funções `async`.
    - ✅ Seguro: Use `asyncio.sleep()`, `httpx.AsyncClient`, `aiofiles` ou delegue código síncrono legado com `await asyncio.to_thread(sync_function, *args)`.
- **Pydantic V2:**
  - Configure `model_config = ConfigDict(from_attributes=True)` em schemas de leitura que serializam modelos SQLAlchemy.
  - Utilize `Field(...)` com restrições claras (ex: `gt=0`, `max_length=255`, `description="..."`).
  - Use `@field_validator` e `@model_validator` com `mode='before'` ou `mode='after'` para validações customizadas.
- **Tratamento Estruturado de Exceções:**
  - Crie uma hierarquia clara de exceções herdando de uma classe base `AppException`.
  - Registre `exception_handler` no FastAPI para converter exceções de domínio em respostas JSON padronizadas com status code adequado.

---

## 2. Clean Architecture & Estrutura de Pacotes

```text
backend/
├── app/
│   ├── main.py                  # Entrypoint FastAPI, Lifespan, Middlewares e Handlers
│   ├── core/                    # Configurações globais e segurança
│   │   ├── config.py            # pydantic-settings (Settings BaseSettings)
│   │   ├── security.py          # JWT, criação de tokens, hashing de senhas
│   │   ├── crypto.py            # Criptografia AES-256-GCM para dados sensíveis
│   │   └── database.py          # async_engine, async_sessionmaker, get_db
│   ├── domain/                  # Entidades de Domínio e Modelos ORM
│   │   ├── models/              # Modelos declarativos SQLAlchemy 2.0 (Mapped)
│   │   └── exceptions.py        # Exceções customizadas de negócio
│   ├── schemas/                 # Schemas Pydantic V2 (Create, Update, Response, Filters)
│   ├── repositories/            # Camada de Acesso a Dados assíncrona (SQLAlchemy)
│   ├── services/                # Regras de negócio, casos de uso e orquestração
│   ├── api/                     # Camada HTTP REST (FastAPI)
│   │   ├── deps.py              # Injeções de dependência compartilhadas (Auth, DB)
│   │   └── v1/
│   │       ├── router.py        # Agregador de rotas v1
│   │       └── endpoints/       # Routers por recurso (ex: users.py, items.py)
│   ├── workers/                 # Processamento em background
│   │   ├── celery_app.py        # Configuração do Celery com broker Redis
│   │   └── tasks.py             # Tarefas @shared_task tipadas
│   └── integrations/            # Clientes de APIs externas, IA e scrapers
├── alembic/                     # Migrações de banco de dados
├── tests/                       # Testes automatizados (pytest-asyncio)
└── pyproject.toml               # Dependências, Ruff, Mypy e Pytest config
```

### 2.1 Routers Enxutos (Thin Routers no FastAPI)
- Endpoints FastAPI têm a responsabilidade estrita de:
  1. Validar a entrada via Schemas Pydantic e receber dependências via `Depends()`.
  2. Obter o usuário autenticado da dependência (`current_user: Annotated[User, Depends(get_current_user)]`).
  3. Invocar a camada de Serviço (`Service`) ou despachar uma tarefa Celery.
  4. Retornar a entidade serializada automaticamente pelo `response_model` com status HTTP adequado (`status.HTTP_201_CREATED`, etc.).

### 2.2 Repositórios SQLAlchemy 2.0 & Prevenção de N+1
- Métodos de repositório devem receber `session: AsyncSession` e executar instruções assíncronas:
  ```python
  from sqlalchemy import select
  from sqlalchemy.orm import selectinload

  async def get_with_relations(self, session: AsyncSession, item_id: int) -> Item | None:
      # Prevenção ativa de N+1 com selectinload:
      stmt = (
          select(Item)
          .options(selectinload(Item.categories), selectinload(Item.author))
          .where(Item.id == item_id)
      )
      result = await session.execute(stmt)
      return result.scalar_one_or_none()
  ```
- **Transações Atômicas:** Em operações que envolvem múltiplas mutações, use transações explícitas com rollback seguro:
  ```python
  async with session.begin():
      session.add(item)
      session.add(audit_log)
      await session.flush()
  ```

---

## 3. Tarefas Assíncronas (Celery + Redis)

- **Desacoplamento:** Qualquer operação de longa duração (envio de e-mails, processamento de relatórios em lote, scraping, chamadas a modelos de IA) DEVE ser executada de forma assíncrona via Celery com Redis como broker.
- **Tipagem e Nomenclatura:** Defina tarefas claras em `app/workers/tasks.py`:
  ```python
  @shared_task(bind=True, max_retries=3, default_retry_delay=60)
  def process_external_sync_task(self, record_id: int) -> dict[str, Any]:
      try:
          ...
      except Exception as exc:
          raise self.retry(exc=exc)
  ```
- **Payloads Limpos:** Envie apenas IDs ou tipos primitivos nos argumentos das tasks Celery; evite serializar objetos SQLAlchemy inteiros como parâmetros.

---

## 4. Frontend Vue 3 + Tailwind CSS v4 + Pinia

- **Composition API:** Utilize `<script setup>` em todos os componentes e telas (`frontend/src/pages/`).
- **Comunicação API:** Utilize o cliente Axios centralizado (`frontend/src/services/api.js`), gerenciando o cabeçalho `Authorization: Bearer <token>` e tratando respostas `401 Unauthorized` com renovação de token ou redirecionamento para login.
- **Tailwind CSS v4:** Aplique classes utilitárias modernas, tema escuro consistente (dark slate / zinc), efeitos de glassmorphism (`backdrop-blur-md bg-slate-900/80 border border-slate-800`), e micro-animações em botões e cards.

---

## 5. 🚨 REGRA CRÍTICA DE ISOLAMENTO DE BANCO DE DADOS EM TESTES

- **PROIBIÇÃO ABSOLUTA**: **NUNCA** execute testes unitários ou scripts automatizados que alterem, limpem (`TRUNCATE`) ou executem drops de tabela no banco de dados principal de desenvolvimento (`POSTGRES_DB=test_pythonfast` ou similar).
- **RISCO GRAVE**: Resetar a base principal apaga dados de desenvolvimento e credenciais de integração do usuário.
- **EXECUÇÃO CORRETA DE TESTES**:
  - Em testes unitários, utilize **Mocks** das classes de Repositório/Serviço ou injeção de dependência via `app.dependency_overrides`.
  - Para testes de integração de banco de dados, utilize **EXCLUSIVAMENTE** uma base de testes dedicada (`POSTGRES_DB=test_pythonfast_test`), transações com rollback automático a cada teste (`nested transaction / savepoint`), ou SQLite async em memória (`sqlite+aiosqlite:///:memory:`).
  - **Comando Permitido**: `pytest -v` (apontando exclusivamente para fixtures com rollback seguro).
  - **Exemplo ESTRITAMENTE PROIBIDO**: Rodar scripts com `Base.metadata.drop_all(bind=engine)` apontando para a base principal ativa do usuário.
