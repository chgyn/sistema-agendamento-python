# 🤖 Antigravity Workspace Rules - Stack Python (FastAPI + Clean Architecture)

Este repositório adota um fluxo orientado a agentes especialistas e práticas modernas de engenharia de software para o ecossistema **Python 3.12+ / FastAPI / SQLAlchemy 2.0 Async / Vue 3**.

---

## 👥 Agentes Especialistas Configurados

Os agentes e suas diretrizes completas estão definidos no diretório [`.agents/`](file:///home/charles/projetos/test-pythonFast/.agents/README.md):

1. **[🏗️ Agente Arquiteto](file:///home/charles/projetos/test-pythonFast/.agents/AGENTE_ARQUITETO.md):** Analisa e propõe planejamento técnico (modelos SQLAlchemy 2.0, endpoints FastAPI, schemas Pydantic V2, jobs Celery, telas Vue 3). **Bloqueia qualquer escrita de código até validação do usuário.**
2. **[⚡ Agente Executor](file:///home/charles/projetos/test-pythonFast/.agents/AGENTE_EXECUTOR.md):** Gera código de produção completo, sem omissões ou placeholders, 100% tipado e assíncrono.
3. **[🔍 Agente Reviewer](file:///home/charles/projetos/test-pythonFast/.agents/AGENTE_REVIEWER.md):** Audita o código gerado quanto a segurança OWASP, integridade do event loop asyncio, prevenção de N+1 no SQLAlchemy, transações atômicas e qualidade frontend.
4. **[📚 Agente Documentador](file:///home/charles/projetos/test-pythonFast/.agents/AGENTE_DOCUMENTADOR.md):** Gera documentação técnica de endpoints, docstrings, changelog e persiste arquivos Markdown no diretório `docs/`.

---

## 📐 Skills do Workspace

- **[fastapi-architecture](file:///home/charles/projetos/test-pythonFast/.agents/skills/fastapi-architecture/SKILL.md):** Guia de Clean Architecture, padrões FastAPI, SQLAlchemy 2.0 Async, Pydantic V2, Celery e Vue 3.

---

## ⚠️ Regras Globais Inegociáveis

1. **Isolamento de Banco de Dados:** NUNCA execute testes ou comandos destrutivos (`drop_all`, `TRUNCATE`) na base de dados principal. Utilize fixtures transacionais com rollback ou bases dedicadas de teste.
2. **Sem Código Parcial:** NUNCA entregue arquivos com trechos omitidos (`# adicione o restante...`).
3. **Asyncio Limpo:** NUNCA execute rotinas síncronas bloqueantes dentro de funções assíncronas sem delegar via `asyncio.to_thread`.
