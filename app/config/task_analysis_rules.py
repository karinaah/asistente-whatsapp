from app.models.task import TaskCategory
from app.models.task import PreferredTimeOfDay

CATEGORY_KEYWORDS: dict[TaskCategory, tuple[str, ...]] = {
    TaskCategory.work: (
        "trabajo",
        "cliente",
        "reunión",
        "reunion",
        "informe",
        "proyecto",
        "correo",
        "presentación",
        "presentacion",
    ),
    TaskCategory.study: (
        "estudiar",
        "estudio",
        "examen",
        "prueba",
        "curso",
        "clase",
        "tarea",
        "aprender",
    ),
    TaskCategory.personal: (
        "familia",
        "amigo",
        "cumpleaños",
        "cumpleanos",
        "casa",
        "personal",
    ),
    TaskCategory.health: (
        "médico",
        "medico",
        "doctor",
        "dentista",
        "ejercicio",
        "gimnasio",
        "salud",
        "medicamento",
    ),
    TaskCategory.errands: (
        "comprar",
        "supermercado",
        "banco",
        "pagar",
        "trámite",
        "tramite",
        "retirar",
        "buscar",
    ),
}

TIME_OF_DAY_KEYWORDS: dict[
    PreferredTimeOfDay,
    tuple[str, ...],
] = {
    PreferredTimeOfDay.morning: (
        "por la mañana",
        "en la mañana",
        "mañana temprano",
    ),
    PreferredTimeOfDay.afternoon: (
        "por la tarde",
        "en la tarde",
    ),
    PreferredTimeOfDay.evening: (
        "por la noche",
        "en la noche",
        "esta noche",
    ),
}