import os

# Utilizar la base de datos de pruebas.
os.environ["AURA_DATABASE_URL"] = "sqlite:///./aura_test.db"

# Registrar todos los modelos SQLAlchemy antes de ejecutar los tests.
import app.models.registry  # noqa: E402, F401