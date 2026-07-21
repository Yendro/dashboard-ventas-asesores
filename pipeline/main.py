import typer
import csv
import logging
from rich.live import Live
from src.config import configurar_logger, OUTPUT_DIR, GLOBAL_CONFIG
from src.bigquery_client import BigQueryClient
from src.token_manager import TokenManager
from src.drive_client import DriveClient
from src.ui import PipelineUI, console

app = typer.Typer(help="Pipeline ETL para el Dashboard de Ventas por Asesor")
logger = configurar_logger()

@app.command()
def update_data():
    """Ejecuta el pipeline ETL: Extracción (BQ), Gestión de Tokens y Carga (Drive)."""
    
    ui = PipelineUI()
    logger.info("--- Iniciando proceso de actualización de datos ---")
    
    with Live(ui.get_renderable(), console=console, refresh_per_second=4) as live:
        
        # 1. Extracción
        ui.update_task(0, "[cyan]RUNNING[/]")
        ui.log("Iniciando conexión a BigQuery...", "cyan")
        live.update(ui.get_renderable())
        
        try:
            bq_client = BigQueryClient()
            dataframes = bq_client.ejecutar_todas_consultas()
            df_desglosadas = dataframes.get('ventas_desglosadas')
            
            if df_desglosadas is None or df_desglosadas.empty:
                raise ValueError("No se extrajeron datos de BigQuery.")
            
            ruta_desglosadas = OUTPUT_DIR / "ventas_desglosadas.json"
            df_desglosadas.to_json(ruta_desglosadas, orient="records", date_format="iso", force_ascii=False)
                
            ui.log(f"Extracción y guardado local exitoso ({len(df_desglosadas)} filas).", "green")
            ui.update_task(0, "[green]OK[/]")
        except Exception as e:
            ui.log(f"Error en Extracción/JSON: {str(e)}", "red")
            ui.update_task(0, "[red]FAIL[/]")
            logger.error(f"Fallo en BQ o JSON: {str(e)}")
            return

        # 2. Gestión de Tokens
        ui.update_task(1, "[cyan]RUNNING[/]")
        ui.log("Sincronizando y validando tokens...", "cyan")
        live.update(ui.get_renderable())
        
        try:
            # Intentar descargar config.json de Drive antes de hacer nada
            drive_client = DriveClient()
            ruta_config = OUTPUT_DIR / "config.json"
            
            if drive_client.descargar_archivo("config.json", ruta_config):
                ui.log("Base de tokens sincronizada desde Drive.", "green")
            else:
                ui.log("No hay tokens en Drive. Se generará base local.", "yellow")

            if 'Asesor' in df_desglosadas.columns:
                asesores_unicos = df_desglosadas['Asesor'].dropna().unique().tolist()
                token_mgr = TokenManager(OUTPUT_DIR)
                
                nuevos_asesores = token_mgr.actualizar_tokens(asesores_unicos)
                
                if nuevos_asesores:
                    ui.log(f"Se crearon {len(nuevos_asesores)} tokens nuevos.", "yellow")
                    ui.update_task(1, "[yellow]WARN[/]") 
                else:
                    ui.log("Tokens validados. No hay cambios.", "green")
                    ui.update_task(1, "[green]OK[/]")
            else:
                ui.log("No se encontró columna 'Asesor'. Omitiendo.", "yellow")
                ui.update_task(1, "[yellow]WARN[/]")
        except Exception as e:
            ui.log(f"Error gestionando Tokens: {str(e)}", "red")
            ui.update_task(1, "[red]FAIL[/]")
            logger.error(f"Fallo en Tokens: {str(e)}")

        # 3. Carga a Drive
        ui.update_task(2, "[cyan]RUNNING[/]")
        ui.log("Conectando con Google Drive API...", "cyan")
        live.update(ui.get_renderable())
        
        try:
            drive_client = DriveClient()
            archivos_a_subir = [ruta_desglosadas, OUTPUT_DIR / "config.json"]
            
            hubo_alertas = False
            for archivo in archivos_a_subir:
                if archivo.exists():
                    exito = drive_client.subir_archivo(archivo)
                    if not exito:
                        hubo_alertas = True
                        ui.log(f"Archivo '{archivo.name}' no encontrado en Drive.", "red")
                    else:
                        ui.log(f"Actualización de '{archivo.name}' exitosa.", "green")
                        
            if hubo_alertas:
                ui.update_task(2, "[yellow]WARN[/]")
                ui.log("Sube los archivos marcados en rojo manualmente por 1ra vez.", "yellow")
            else:
                ui.update_task(2, "[green]OK[/]")
                ui.log("--- Pipeline finalizada con éxito ---", "bold green")
                
        except Exception as e:
            ui.log(f"Error conectando a Drive: {str(e)}", "red")
            ui.update_task(2, "[red]FAIL[/]")
            logger.error(f"Fallo en Drive: {str(e)}")
            return

        live.update(ui.get_renderable())

@app.command()
def init():
    """Descarga los archivos de Google Drive para preparar un entorno local nuevo."""
    console.print("\n[bold cyan]Sincronizando entorno local con Google Drive...[/]")
    try:
        drive_client = DriveClient()
        archivos = ["config.json", "ventas_desglosadas.json"]
        
        for archivo in archivos:
            ruta = OUTPUT_DIR / archivo
            if drive_client.descargar_archivo(archivo, ruta):
                console.print(f"[green]✓ {archivo} descargado exitosamente.[/]")
            else:
                console.print(f"[yellow]⚠️ {archivo} no existe en Drive aún.[/]")
                
        console.print("[bold green]\nEntorno inicializado correctamente.[/]")
    except Exception as e:
        console.print(f"[bold red]✗ Error inicializando el entorno: {str(e)}[/]")

@app.command()
def export_links():
    """Genera un archivo CSV local con los asesores y sus tokens de acceso."""
    
    # Extraer la URL base (traerá un valor de relleno si no está configurada)
    base_url = GLOBAL_CONFIG.get("WEBAPP_BASE_URL")
    if "URL_PENDIENTE" in base_url:
        console.print("[yellow]Aviso: La variable WEBAPP_BASE_URL no está configurada en tu .env.[/]")
        console.print("[yellow]Los links se generarán con una URL de relleno provisional.[/]\n")
    
    # Asegurarnos de que termine en token= 
    if not base_url.endswith("token="):
        base_url = base_url.rstrip("/") + "?token=" if "?" not in base_url else base_url + "&token="
    
    token_mgr = TokenManager(OUTPUT_DIR)
    tokens_actuales = token_mgr.tokens
    
    if not tokens_actuales:
        console.print("[red]No hay tokens registrados. Ejecuta 'update-data' primero.[/]")
        return
        
    ruta_csv = OUTPUT_DIR / "links_asesores.csv"
    
    try:
        with open(ruta_csv, mode="w", encoding="utf-8", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["Asesor", "Link de Acceso"])
            
            for asesor, token in tokens_actuales.items():
                link_completo = f"{base_url}{token}"
                writer.writerow([asesor, link_completo])
                
        console.print(f"[bold green]✓ CSV generado exitosamente en: {ruta_csv}[/]")
        
    except Exception as e:
        console.print(f"[bold red]✗ Error al generar el CSV: {str(e)}[/]")

if __name__ == "__main__":
    app()