from sqlalchemy.ext.asyncio import AsyncSession
from app.core.config import settings
from app.core.security import verify_password, create_access_token
from app.domain.exceptions import UnauthorizedError
from app.domain.models.user import User
from app.repositories.user_repository import UserRepository
from app.schemas.auth import LoginRequest, TokenResponse


class AuthService:
    def __init__(self, user_repo: UserRepository | None = None):
        self.user_repo = user_repo or UserRepository()

    async def authenticate(self, session: AsyncSession, login_data: LoginRequest) -> TokenResponse:
        user = await self.user_repo.get_by_email(session, login_data.email)
        if not user or not user.is_active:
            raise UnauthorizedError("E-mail ou senha inválidos.")

        if not verify_password(login_data.password, user.password_hash):
            raise UnauthorizedError("E-mail ou senha inválidos.")

        token = create_access_token(subject=str(user.id))
        return TokenResponse(
            access_token=token,
            expires_in=settings.ACCESS_TOKEN_EXPIRE_MINUTES * 60,
        )
