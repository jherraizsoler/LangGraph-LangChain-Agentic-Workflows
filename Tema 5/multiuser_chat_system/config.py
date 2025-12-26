import os

# Configuración de directorios
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, "data")
USERS_DIR = os.path.join(BASE_DIR, "users")

# Crear directorios si no existen
os.makedirs(DATA_DIR, exist_ok=True)
os.makedirs(USERS_DIR, exist_ok=True)

# Configuración del modelo
DEFAULT_MODEL = "gpt-4o-mini"
DEFAULT_TEMPERATURE = 0.3

# Configuración de memoria
MAX_VECTOR_RESULTS = 3
MEMORY_CATEGORIES = [
    "personal",
    "profesional",
    "preferencias",
    "hechos_importantes"
]

# Configuración de la interfaz
PAGE_TITLE = "Chat Multi-Usuario con memoria Avanzada"
PAGE_ICON = "🤖"