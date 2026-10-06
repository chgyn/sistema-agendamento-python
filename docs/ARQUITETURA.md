# 🏗️ Arquitetura do Sistema de Agendamento

## 1. Visão Geral
O sistema é um **monolito modular multi-tenant** desenvolvido com **Python 3.12+ / FastAPI** no backend e **Vue 3 (Vite + TypeScript + Tailwind CSS v4)** no frontend. O objetivo é fornecer gerenciamento completo de agendamentos para barbearias, salões de beleza e negócios similares, garantindo isolamento estrito de dados entre diferentes estabelecimentos.

---

## 2. Padrões de Projeto & Princípios
- **Clean Architecture & Hexagonal Architecture:** Regras de negócio desacopladas do framework web (FastAPI) e do driver de banco de dados.
- **SOLID:** Alta coesão e baixo acoplamento entre módulos.
- **Repository Pattern Assíncrono:** Centralização do acesso a dados em repositórios tipados do SQLAlchemy 2.0.
- **Service Layer (Use Cases):** Orquestração dos fluxos de negócio, cálculos de slots e prevenção de concorrência.
- **Prevenção Ativa de N+1:** Todos os modelos SQLAlchemy declaram relacionamentos com `lazy="raise"` e utilizam carregamento explícito via `options(selectinload(...))` nos repositórios.

---

## 3. Isolamento Multi-Tenant
A aplicação adota o modelo **Multi-Tenant Lógico** com isolamento no nível da camada de persistência:
- Cada estabelecimento possui um `id` (UUID único) e um `slug` (para URL pública).
- Todas as entidades internas (`User`, `Service`, `Professional`, `Customer`, `Appointment`) possuem a chave estrangeira `establishment_id`.
- Em qualquer endpoint autenticado, a dependência `get_current_user` extrai o tenant a partir do token JWT assinado, e o repositório filtra explicitamente por `establishment_id == current_user.establishment_id`.
- Isso impede vulnerabilidades de IDOR (*Insecure Direct Object References*), onde a alteração de um ID na requisição daria acesso a dados de outro lojista.

---

## 4. Controle de Concorrência & Prevenção de "Double-Booking"
O controle de disponibilidade é uma parte crítica do sistema:
- O cálculo de slots livres é realizado pelo `AvailabilityService`, cruzando a grade semanal de expediente (`ProfessionalWorkingHour`), pausas de almoço/descanso, períodos de indisponibilidade (`ProfessionalUnavailability`) e agendamentos existentes no dia.
- No momento da reserva (`AppointmentService.create_public_appointment`), o sistema abre uma transação atômica e executa a verificação de sobreposição:
  ```sql
  SELECT * FROM appointments 
  WHERE professional_id = :p 
    AND status != 'CANCELLED' 
    AND start_datetime < :novo_fim 
    AND end_datetime > :novo_inicio
  FOR UPDATE;
  ```
- No PostgreSQL, a cláusula `FOR UPDATE` bloqueia a verificação simultânea no banco. Caso ocorra colisão, uma exceção `AppointmentConflictError` é disparada retornando **HTTP 409 Conflict**, garantindo que apenas uma transação obtenha sucesso.

---

## 5. Estrutura de Pacotes do Backend
```text
backend/
├── app/
│   ├── main.py                  # Entrypoint FastAPI, CORS e Exception Handlers globais
│   ├── core/                    # Configurações, Segurança JWT, AES-256-GCM e Conexão DB
│   │   ├── config.py
│   │   ├── security.py
│   │   ├── crypto.py
│   │   └── database.py
│   ├── domain/                  # Modelos SQLAlchemy 2.0 e Exceções de Domínio
│   │   ├── exceptions.py
│   │   └── models/
│   ├── schemas/                 # Schemas Pydantic V2 (Request, Response, DTOs)
│   ├── repositories/            # Camada de Acesso a Dados assíncrona
│   ├── services/                # Regras de Negócio e Casos de Uso
│   ├── api/                     # Rotas e Injeção de Dependências
│   │   ├── deps.py
│   │   └── v1/
│   └── workers/                 # Processamento em Background com Celery e Redis
│       ├── celery_app.py
│       └── tasks.py
├── alembic/                     # Migrações versionadas do banco de dados
├── scripts/                     # Scripts auxiliares (Seed de demonstração)
└── tests/                       # Testes automatizados (pytest-asyncio)
```
