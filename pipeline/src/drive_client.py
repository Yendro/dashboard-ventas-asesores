import logging
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
from config import GLOBAL_CONFIG

logger = logging.getLogger(__name__)

class DriveClient:
    def __init__(self):
        self.credentials_path = Path(GLOBAL_CONFIG["DRIVE_CREDENTIALS_PATH"])
        self.folder_id = GLOBAL_CONFIG["DRIVE_FOLDER_ID"]
        self.service = self._autenticar()

    def _autenticar(self):
        try:
            # Notar que el scope cambia a Drive
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            logger.info("Conexión a Google Drive establecida.")
            return build('drive', 'v3', credentials=credentials)
        except Exception as e:
            logger.error(f"Error autenticando con Drive: {e}")
            raise

    def _buscar_archivo(self, nombre_archivo: str) -> str:
        """Busca un archivo por nombre dentro de la carpeta destino y retorna su ID."""
        query = f"'{self.folder_id}' in parents and name='{nombre_archivo}' and trashed=false"
        resultados = self.service.files().list(q=query, spaces='drive', fields='files(id, name)').execute()
        archivos = resultados.get('files', [])
        return archivos[0]['id'] if archivos else None

    def subir_archivo(self, ruta_archivo: Path):
        nombre_archivo = ruta_archivo.name
        archivo_id = self._buscar_archivo(nombre_archivo)
        
        media = MediaFileUpload(ruta_archivo, mimetype='application/json', resumable=True)

        try:
            if archivo_id:
                logger.info(f"Actualizando {nombre_archivo} en Drive...")
                self.service.files().update(
                    fileId=archivo_id,
                    media_body=media
                ).execute()
            else:
                logger.info(f"Creando {nombre_archivo} en Drive...")
                file_metadata = {'name': nombre_archivo, 'parents': [self.folder_id]}
                self.service.files().create(
                    body=file_metadata,
                    media_body=media,
                    fields='id'
                ).execute()
            logger.info(f"✓ Subida de {nombre_archivo} completada.")
        except Exception as e:
            logger.error(f"Error subiendo {nombre_archivo}: {e}")
            raise