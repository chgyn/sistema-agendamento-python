import uuid
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.security import get_password_hash
from app.domain.exceptions import EntityNotFoundError, EntityAlreadyExistsError
from app.domain.models.establishment import Establishment
from app.domain.models.user import User, UserRole
from app.repositories.establishment_repository import EstablishmentRepository
from app.repositories.user_repository import UserRepository
from app.schemas.establishment import EstablishmentCreate, EstablishmentUpdate, EstablishmentResponse


class EstablishmentService:
    def __init__(
        self,
        establishment_repo: EstablishmentRepository | None = None,
        user_repo: UserRepository | None = None,
    ):
        self.establishment_repo = establishment_repo or EstablishmentRepository()
        self.user_repo = user_repo or UserRepository()

    async def get_by_id(self, session: AsyncSession, establishment_id: uuid.UUID) -> Establishment:
        est = await self.establishment_repo.get_by_id(session, establishment_id)
        if not est:
            raise EntityNotFoundError("Estabelecimento", establishment_id)
        return est

    async def get_by_slug(self, session: AsyncSession, slug: str) -> Establishment:
        est = await self.establishment_repo.get_by_slug(session, slug)
        if not est or not est.is_active:
            raise EntityNotFoundError("Estabelecimento", slug)
        return est

    async def create_with_admin(
        self,
        session: AsyncSession,
        establishment_in: EstablishmentCreate,
        admin_name: str,
        admin_email: str,
        admin_password: str,
    ) -> Establishment:
        existing_slug = await self.establishment_repo.get_by_slug(session, establishment_in.slug)
        if existing_slug:
            raise EntityAlreadyExistsError("Estabelecimento", "slug", establishment_in.slug)

        existing_user = await self.user_repo.get_by_email(session, admin_email)
        if existing_user:
            raise EntityAlreadyExistsError("Usuário", "email", admin_email)

        async with session.begin_nested():
            establishment = Establishment(
                name=establishment_in.name,
                slug=establishment_in.slug,
                email=establishment_in.email,
                phone=establishment_in.phone,
                address=establishment_in.address,
                settings=establishment_in.settings,
            )
            session.add(establishment)
            await session.flush()

            admin_user = User(
                establishment_id=establishment.id,
                name=admin_name,
                email=admin_email,
                password_hash=get_password_hash(admin_password),
                role=UserRole.ADMIN,
                is_active=True,
            )
            session.add(admin_user)
            await session.flush()

        await session.commit()
        await session.refresh(establishment)
        return establishment

    async def update(
        self, session: AsyncSession, establishment_id: uuid.UUID, data: EstablishmentUpdate
    ) -> Establishment:
        est = await self.get_by_id(session, establishment_id)
        update_data = data.model_dump(exclude_unset=True)
        for key, value in update_data.items():
            setattr(est, key, value)
        await self.establishment_repo.update(session, est)
        await session.commit()
        return est
