import os
import sys
import logging
from datetime import datetime
from pathlib import Path
from dotenv import load_dotenv

# Cargar variables de entorno inmediatamente
load_dotenv()

# Rutas base
BASE_DIR = Path(__file__).resolve().parent.parent
DATA_DIR = BASE_DIR / "data"
OUTPUT_DIR = BASE_DIR / "output"
LOGS_DIR = BASE_DIR / "logs"


# Asegurar que existan los directorios
OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)


# Crear un nombre único para el log de esta ejecución.
EXECUTION_TIMESTAMP = datetime.now().strftime("%Y%m%d_%H%M")
LOG_FILE = LOGS_DIR / f"job_{EXECUTION_TIMESTAMP}.log"


# Configuración global estricta
VARIABLES_REQUERIDAS = [
    "BIGQUERY_CREDENTIALS_PATH",
    "BIGQUERY_PROJECT_ID",
    "DRIVE_CREDENTIALS_PATH",
    "DRIVE_FOLDER_ID",
]

GLOBAL_CONFIG = {}

for var in VARIABLES_REQUERIDAS:
    valor = os.getenv(var)

    if not valor:
        print(
            f"CRITICAL ERROR: Falta la variable de entorno obligatoria "
            f"'{var}' en el archivo .env"
        )
        sys.exit(1)

    GLOBAL_CONFIG[var] = valor


def configurar_logger() -> logging.Logger:
    """
    Configura el logger general de la aplicación.

    En cada ejecución se crea un archivo nuevo dentro de la carpeta `logs`.
    Los mensajes también se muestran en la terminal.
    """
    logger = logging.getLogger()
    logger.setLevel(logging.INFO)

    # Evita agregar handlers duplicados si la función se llama varias veces
    # durante la misma ejecución.
    if not getattr(logger, "_logger_configurado", False):
        formatter = logging.Formatter(
            "%(asctime)s - %(levelname)s - %(message)s",
            datefmt="%Y-%m-%d %H:%M",
        )

        file_handler = logging.FileHandler(
            filename=LOG_FILE,
            mode="a",
            encoding="utf-8",
        )
        file_handler.setLevel(logging.INFO)
        file_handler.setFormatter(formatter)

        stream_handler = logging.StreamHandler(sys.stdout)
        stream_handler.setLevel(logging.INFO)
        stream_handler.setFormatter(formatter)

        logger.addHandler(file_handler)
        logger.addHandler(stream_handler)

        # Bandera personalizada para no duplicar handlers.
        logger._logger_configurado = True  # type: ignore[attr-defined]

        logger.info("Inicio de ejecución")
        logger.info("Archivo de log: %s", LOG_FILE)

    return logger