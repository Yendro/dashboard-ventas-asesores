import io
import logging
from pathlib import Path
from google.oauth2 import service_account
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload, MediaIoBaseDownload
from src.config import GLOBAL_CONFIG

logger = logging.getLogger(__name__)

class DriveClient:
    def __init__(self) -> None:
        self.credentials_path = Path(GLOBAL_CONFIG["DRIVE_CREDENTIALS_PATH"])
        self.folder_id = GLOBAL_CONFIG["DRIVE_FOLDER_ID"]
        self.service = self._autenticar()

    def _autenticar(self):
        """Autentica la cuenta de servicio y construye el cliente de Drive."""
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/drive"]
            )
            service = build('drive', 'v3', credentials=credentials, cache_discovery=False)
            logger.info("Conexión a Google Drive establecida.")
            return service
        except Exception as e:
            logger.error(f"Error autenticando con Drive: {e}")
            raise

    @staticmethod
    def _escapar_valor_query(valor: str) -> str:
        """Escapa caracteres especiales usados en consultas `q` de Drive."""
        return valor.replace("\\", "\\\\").replace("'", "\\'")

    def _buscar_archivo(self, nombre_archivo: str) -> str | None:
        """Busca un archivo por nombre dentro de la carpeta destino y retorna su ID."""
        nombre_seguro = self._escapar_valor_query(nombre_archivo)
        query = f"'{self.folder_id}' in parents and name='{nombre_seguro}' and trashed=false"
        resultados = (
            self.service.files()
            .list(
                q=query,
                spaces="drive",
                fields="files(id, name)",
                pageSize=1,
                supportsAllDrives=True,
                includeItemsFromAllDrives=True,
            )
            .execute()
        )
        archivos = resultados.get('files', [])
        return archivos[0]['id'] if archivos else None
    
    def descargar_archivo(self, nombre_archivo: str, ruta_destino: Path) -> bool:
        """
        Descarga un archivo desde Drive y lo guarda localmente.
        Retorna True si fue exitoso, False si no existe en Drive.
        """
        try:
            archivo_id = self._buscar_archivo(nombre_archivo)
            
            if not archivo_id:
                return False

            request = self.service.files().get_media(fileId=archivo_id)
            fh = io.FileIO(ruta_destino, 'wb')
            downloader = MediaIoBaseDownload(fh, request)
            
            done = False
            while done is False:
                status, done = downloader.next_chunk()
                
            return True
        except Exception as e:
            logger.error(f"Error descargando {nombre_archivo}: {e}")
            return False

    def subir_archivo(self, ruta_archivo: Path) -> bool:
        """
        Actualiza un archivo que ya existe en la carpeta configurada de Drive.
        Retorna True si fue exitoso, False si no encontró el archivo y requiere carga manual.
        """
        ruta_archivo = Path(ruta_archivo)

        if not ruta_archivo.is_file():
            logger.error(f"No existe el archivo local que se intentó subir: {ruta_archivo}")
            return False

        nombre_archivo = ruta_archivo.name

        try:
            archivo_id = self._buscar_archivo(nombre_archivo)

            if not archivo_id:
                mensaje = (
                    f"\n⚠️ ATENCIÓN: No se actualizó '{nombre_archivo}' en Drive.\n"
                    f"  -> El archivo no existe actualmente en la carpeta destino de Drive.\n"
                    f"  -> ACCIÓN: Sube manualmente el output local a Drive por única vez y "
                    f"asegúrate de que esté compartido con el correo de la cuenta de servicio.\n"
                    f"  -> Las próximas ejecuciones de la pipeline lo detectarán y actualizarán automáticamente.\n"
                )
                logger.warning(mensaje)
                return False

            media = MediaFileUpload(
                filename=str(ruta_archivo),
                mimetype="application/json",
                resumable=True,
            )

            logger.info(f"Actualizando {nombre_archivo} en Drive...")

            self.service.files().update(
                fileId=archivo_id,
                media_body=media,
                supportsAllDrives=True,
                fields="id, name, modifiedTime",
            ).execute()

            logger.info(f"✓ Subida de {nombre_archivo} completada.")
            return True

        except Exception as e:
            logger.error(f"Error inesperado subiendo {nombre_archivo}: {str(e)}")
            return False