import typer
import logging
from config import configurar_logger, OUTPUT_DIR
from src.bigquery_client import BigQueryClient
from src.token_manager import TokenManager
from src.drive_client import DriveClient

app = typer.Typer(help="Pipeline ETL para el Dashboard de Ventas por Asesor")
logger = configurar_logger()

@app.command()
def update_data():
    """Ejecuta el pipeline completo: Extrae (BQ), Transforma (JSON), Sube (Drive)."""
    logger.info("--- Iniciando proceso de actualización de datos ---")
    
    # 1. Extracción
    bq_client = BigQueryClient()
    dataframes = bq_client.ejecutar_todas_consultas()
    
    if not dataframes:
        logger.error("No se extrajeron datos. Abortando pipeline.")
        raise typer.Exit(code=1)
        
    df_agrupadas = dataframes.get('ventas_agrupadas')
    df_desglosadas = dataframes.get('ventas_desglosadas')
    
    if df_desglosadas is None or df_agrupadas is None:
         logger.error("Faltan las consultas requeridas en data/src.")
         raise typer.Exit(code=1)

    # 2. Transformación a JSON 
    logger.info("Transformando datos a formato JSON...")
    ruta_agrupadas = OUTPUT_DIR / "ventas_agrupadas.json"
    ruta_desglosadas = OUTPUT_DIR / "ventas_desglosadas.json"
    
    try:
        # Date_format='iso' previene errores de serialización de fechas en Javascript
        df_agrupadas.to_json(ruta_agrupadas, orient="records", date_format="iso", force_ascii=False)
        df_desglosadas.to_json(ruta_desglosadas, orient="records", date_format="iso", force_ascii=False)
        logger.info("✓ Archivos JSON generados correctamente.")
    except Exception as e:
        logger.error(f"✗ Error crítico al transformar los DataFrames a JSON: {str(e)}")
        raise typer.Exit(code=1) # Detenemos la ejecución para no subir archivos corruptos

    # 3. Gestión de Tokens
    logger.info("Gestionando tokens de asesores...")
    try:
        if 'Asesor' in df_desglosadas.columns:
            asesores_unicos = df_desglosadas['Asesor'].dropna().unique().tolist()
            token_mgr = TokenManager(OUTPUT_DIR)
            token_mgr.actualizar_tokens(asesores_unicos)
            logger.info("✓ Tokens actualizados correctamente.")
        else:
            logger.warning("No se encontró la columna 'Asesor'. Se omitió la generación de tokens.")
    except Exception as e:
        logger.error(f"✗ Error al gestionar los tokens: {str(e)}")
        raise typer.Exit(code=1)

    # 4. Carga a Drive
    logger.info("Subiendo archivos a Google Drive...")
    try:
        drive_client = DriveClient()
        archivos_a_subir = [ruta_agrupadas, ruta_desglosadas, OUTPUT_DIR / "config.json"]
        
        for archivo in archivos_a_subir:
            if archivo.exists():
                drive_client.subir_archivo(archivo)
                
        logger.info("--- Pipeline finalizada con éxito ---")
    except Exception as e:
        logger.error(f"✗ Error durante la carga de archivos a Drive: {str(e)}")
        raise typer.Exit(code=1)

if __name__ == "__main__":
    app()