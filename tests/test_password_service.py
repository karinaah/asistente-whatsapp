from app.services.password_service import PasswordService


def test_hash_password_uses_argon2id():
    service = PasswordService()

    password_hash = service.hash_password("Aura-Prueba-2026!")

    assert password_hash.startswith("$argon2id$")
    assert password_hash != "Aura-Prueba-2026!"


def test_verify_correct_password():
    service = PasswordService()

    password = "Aura-Prueba-2026!"
    password_hash = service.hash_password(password)

    assert service.verify_password(password, password_hash) is True


def test_reject_incorrect_password():
    service = PasswordService()

    password_hash = service.hash_password("Aura-Prueba-2026!")

    assert service.verify_password(
        "ClaveIncorrecta",
        password_hash,
    ) is False


def test_reject_invalid_hash():
    service = PasswordService()

    assert service.verify_password(
        "Aura-Prueba-2026!",
        "hash_invalido",
    ) is False


def test_same_password_generates_different_hashes():
    service = PasswordService()

    password = "Aura-Prueba-2026!"

    first_hash = service.hash_password(password)
    second_hash = service.hash_password(password)

    assert first_hash != second_hash
    assert service.verify_password(password, first_hash)
    assert service.verify_password(password, second_hash)