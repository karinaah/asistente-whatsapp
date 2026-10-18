from argon2 import PasswordHasher
from argon2.exceptions import InvalidHashError, VerifyMismatchError, VerificationError


class PasswordService:
    """Servicio para proteger y verificar contraseñas con Argon2id."""

    def __init__(self):
        self._hasher = PasswordHasher()

    def hash_password(self, password: str) -> str:
        """Genera un hash seguro de una contraseña."""
        return self._hasher.hash(password)

    def verify_password(self, password: str, password_hash: str) -> bool:
        """Comprueba una contraseña contra su hash."""
        try:
            return self._hasher.verify(password_hash, password)
        except (VerifyMismatchError, VerificationError, InvalidHashError):
            return False