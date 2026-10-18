from sqlalchemy.orm import Session

from app.models.user_db import UserDB
from app.repositories.user_repository import UserRepository
from sqlalchemy.exc import IntegrityError

from app.services.password_service import PasswordService

class UserService:
    def __init__(
        self,
        repository: UserRepository | None = None,
    ):
        self.repository = (
            repository
            or UserRepository()
        )

    def create_user(
        self,
        db: Session,
        name: str | None = None,
    ) -> UserDB:
        return self.repository.create(
            db,
            name=name,
        )

    def get_user(
        self,
        db: Session,
        user_id: int,
    ) -> UserDB | None:
        return self.repository.get_by_id(
            db,
            user_id=user_id,
        )

    def register_user(
        self,
        db: Session,
        email: str,
        password: str,
        name: str | None = None,
    ) -> UserDB:
        """Registra un usuario con correo y contraseña."""

        normalized_email = email.strip().lower()

        if not normalized_email or "@" not in normalized_email:
            raise ValueError("Correo electrónico inválido")

        if len(normalized_email) > 254:
            raise ValueError("Correo electrónico demasiado largo")

        if len(password) < 12:
            raise ValueError(
                "La contraseña debe tener al menos 12 caracteres"
            )

        existing_user = self.repository.get_by_email(
            db,
            normalized_email,
        )

        if existing_user is not None:
            raise ValueError("El correo ya está registrado")

        password_hash = PasswordService().hash_password(password)

        try:
            return self.repository.create(
                db,
                name=name,
                email=normalized_email,
                password_hash=password_hash,
            )
        except IntegrityError:
            db.rollback()
            raise ValueError("El correo ya está registrado") from None

    def authenticate_user(
        self,
        db: Session,
        email: str,
        password: str,
    ) -> UserDB | None:
        """Autentica un usuario mediante correo y contraseña."""

        normalized_email = email.strip().lower()

        user = self.repository.get_by_email(
            db,
            normalized_email,
        )

        if user is None or not user.password_hash:
            return None

        password_service = PasswordService()

        if not password_service.verify_password(
            password,
            user.password_hash,
        ):
            return None

        return user