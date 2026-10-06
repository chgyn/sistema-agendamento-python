from fastapi import APIRouter
from app.api.v1.endpoints import (
    auth,
    public,
    establishment,
    services,
    professionals,
    appointments,
    customers,
)

api_router = APIRouter()

api_router.include_router(auth.router, prefix="/auth", tags=["Autenticação"])
api_router.include_router(public.router, prefix="/public", tags=["Público (Cliente)"])
api_router.include_router(establishment.router, prefix="/establishment", tags=["Estabelecimento"])
api_router.include_router(services.router, prefix="/services", tags=["Serviços"])
api_router.include_router(professionals.router, prefix="/professionals", tags=["Profissionais"])
api_router.include_router(appointments.router, prefix="/appointments", tags=["Agendamentos"])
api_router.include_router(customers.router, prefix="/customers", tags=["Clientes"])
