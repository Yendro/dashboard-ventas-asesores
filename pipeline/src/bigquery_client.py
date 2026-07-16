import logging
import pandas as pd
from pathlib import Path
from typing import Dict, Optional
from google.cloud import bigquery
from google.oauth2 import service_account
from config import GLOBAL_CONFIG, SQL_DIR

logger = logging.getLogger(__name__)

class BigQueryClient:
    def __init__(self):
        self.credentials_path = Path(GLOBAL_CONFIG["BIGQUERY_CREDENTIALS_PATH"])
        self.project_id = GLOBAL_CONFIG["BIGQUERY_PROJECT_ID"]
        self.sql_folder = SQL_DIR
        self.client: Optional[bigquery.Client] = None
        
    def conectar(self) -> None:
        try:
            credentials = service_account.Credentials.from_service_account_file(
                self.credentials_path,
                scopes=["https://www.googleapis.com/auth/cloud-platform"]
            )
            self.client = bigquery.Client(
                credentials=credentials,
                project=self.project_id
            )
            logger.info("Conexión a BigQuery establecida exitosamente.")
        except Exception as e:
            logger.error(f"Error conectando a BigQuery: {str(e)}")
            raise
    
    def ejecutar_consulta(self, sql_file: Path) -> pd.DataFrame:
        if not self.client:
            self.conectar()
        with open(sql_file, 'r', encoding='utf-8') as f:
            sql = f.read()
            
        logger.info(f"Ejecutando consulta: {sql_file.name}")
        df = self.client.query(sql).result().to_dataframe()
        return df
    
    def ejecutar_todas_consultas(self) -> Dict[str, pd.DataFrame]:
        if not self.sql_folder.exists():
            logger.warning(f"La carpeta SQL no existe: {self.sql_folder}")
            return {}
            
        archivos_sql = list(self.sql_folder.glob('*.sql'))
        resultados = {}
        
        for sql_file in archivos_sql:
            try:
                # Usa el nombre del archivo (ej. 'ventas_agrupadas') como llave
                resultados[sql_file.stem] = self.ejecutar_consulta(sql_file)
            except Exception as e:
                logger.error(f"✗ Error en {sql_file.name}: {str(e)}")
                
        return resultados