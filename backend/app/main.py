from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from fastapi.exceptions import RequestValidationError
from app.core.config import settings
from app.domain.exceptions import AppException
from app.api.v1.router import api_router


@asynccontextmanager
async def lifespan(app: FastAPI):
    # Inicialização assíncrona (lifespan)
    yield
    # Finalização de recursos / encerramento de conexões


app = FastAPI(
    title=settings.PROJECT_NAME,
    description="API REST Multi-tenant para Agendamento de Barbearias e Salões de Beleza em Clean Architecture",
    version="1.0.0",
    docs_url="/docs",
    redoc_url="/redoc",
    openapi_url="/openapi.json",
    lifespan=lifespan,
)

# Configuração de CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.BACKEND_CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# Exception handler global para exceções de domínio estruturadas
@app.exception_handler(AppException)
async def app_exception_handler(request: Request, exc: AppException) -> JSONResponse:
    return JSONResponse(
        status_code=exc.status_code,
        content={
            "error": True,
            "message": exc.message,
            "details": exc.details,
            "type": exc.__class__.__name__,
        },
    )


# Exception handler padronizado para erros de validação Pydantic V2
@app.exception_handler(RequestValidationError)
async def validation_exception_handler(request: Request, exc: RequestValidationError) -> JSONResponse:
    errors = []
    for err in exc.errors():
        loc = " -> ".join([str(p) for p in err.get("loc", [])])
        msg = err.get("msg", "Erro de validação")
        errors.append({"field": loc, "message": msg})

    return JSONResponse(
        status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
        content={
            "error": True,
            "message": "Dados de requisição inválidos.",
            "details": errors,
            "type": "RequestValidationError",
        },
    )


# Rota de verificação de integridade (Health Check)
@app.get("/health", tags=["Health"])
async def health_check():
    return {
        "status": "healthy",
        "project": settings.PROJECT_NAME,
        "environment": settings.ENVIRONMENT,
    }


# Inclusão das rotas da API v1
app.include_router(api_router, prefix=settings.API_V1_STR)
