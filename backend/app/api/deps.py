from typing import Annotated
import uuid
from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import get_db
from app.core.security import decode_access_token
from app.domain.exceptions import UnauthorizedError, ForbiddenError
from app.domain.models.user import User, UserRole
from app.repositories.user_repository import UserRepository

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/api/v1/auth/login")

DbSession = Annotated[AsyncSession, Depends(get_db)]
TokenDep = Annotated[str, Depends(oauth2_scheme)]


async def get_current_user(session: DbSession, token: TokenDep) -> User:
    """Valida o token JWT e retorna o usuário logado com seu tenant."""
    payload = decode_access_token(token)
    if not payload or "sub" not in payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Token de autenticação inválido ou expirado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    try:
        user_id = uuid.UUID(payload["sub"])
    except ValueError:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Identificador de usuário inválido no token.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    user_repo = UserRepository()
    user = await user_repo.get_by_id(session, user_id)
    if not user or not user.is_active:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Usuário inativo ou não encontrado.",
            headers={"WWW-Authenticate": "Bearer"},
        )

    return user


CurrentUser = Annotated[User, Depends(get_current_user)]


def require_role(role: UserRole):
    """Dependência para autorização baseada em perfil de acesso (Role-Based Access Control)."""
    async def role_checker(current_user: CurrentUser) -> User:
        if current_user.role != role:
            raise HTTPException(
                status_code=status.HTTP_403_FORBIDDEN,
                detail=f"Operação restrita para usuários com perfil {role.value}.",
            )
        return current_user

    return role_checker
