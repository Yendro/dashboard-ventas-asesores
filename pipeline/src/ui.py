from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

# Instancia global de la consola para imprimir elementos enriquecidos
console = Console()

class PipelineUI:
    """
    Controla la interfaz gráfica en la terminal durante la ejecución del pipeline.
    Utiliza un diseño de dos columnas:
      - Izquierda: Estado actual de cada módulo (OK, RUNNING, FAIL).
      - Derecha: Registro en vivo de los eventos y errores (Logs).
    """
    def __init__(self):
        # Módulos fijos que componen la tabla de la izquierda.
        self.tasks = [
            {"id": "01", "mod": "bigquery_client.py", "status": "[dim]WAIT[/]"},
            {"id": "02", "mod": "token_manager.py", "status": "[dim]WAIT[/]"},
            {"id": "03", "mod": "drive_client.py", "status": "[dim]WAIT[/]"}
        ]
        
        # Almacena el historial de logs para mostrarlos en el panel derecho.
        self.logs = []

    def update_task(self, idx: int, status: str):
        """
        Actualiza el estado de un módulo en la tabla visual.
        
        Args:
            idx (int): Índice del módulo (0: BQ, 1: Tokens, 2: Drive).
            status (str): Etiqueta con formato Rich (ej. "[green]OK[/]").
        """
        self.tasks[idx]["status"] = status

    def log(self, message: str, style="white"):
        """
        Inyecta un nuevo mensaje en el panel de logs.
        Mantiene un límite estricto de mensajes para evitar que la interfaz
        crezca verticalmente y empuje la línea de comandos hacia abajo.
        
        Args:
            message (str): El texto del evento a registrar.
            style (str): El color o estilo del texto (ej. "red", "bold green").
        """
        self.logs.append(f"[{style}]{message}[/]")
        if len(self.logs) > 13:
            self.logs.pop(0)

    def get_renderable(self):
        """
        Ensambla y retorna el componente visual completo.
        Se utiliza Table.grid() en lugar de Layout() para garantizar que la
        interfaz solo ocupe el alto estrictamente necesario, evitando saltos
        de línea masivos al finalizar el script.
        """
        # --- 1. Panel Izquierdo: Tabla de Estatus ---
        # Se remueven los bordes internos para un look más limpio.
        status_table = Table(box=None, expand=True)
        status_table.add_column("id", style="bold yellow", width=4)
        status_table.add_column("module", style="bold white")
        status_table.add_column("status", justify="right", width=10)
        
        for task in self.tasks:
            status_table.add_row(task["id"], task["mod"], task["status"])
            
        panel_status = Panel(
            status_table, 
            title="[bold cyan]Pipeline status[/]", 
            border_style="cyan", 
            height=15
        )

        # --- 2. Panel Derecho: Historial de Logs ---
        log_text = Text.from_markup("\n".join(self.logs))
        
        panel_logs = Panel(
            log_text, 
            title="[bold cyan]Execution Logs[/]", 
            border_style="cyan", 
            height=15
        )

        # --- 3. Grid invisible de 2 columnas sin forzar a la terminal a expandirse verticalmente.
        master_grid = Table.grid(expand=True)
        master_grid.add_column(ratio=1) # Columna izquierda (1 tercio)
        master_grid.add_column(ratio=2) # Columna derecha (2 tercios)
        
        # Insertamos ambos paneles en una sola fila
        master_grid.add_row(panel_status, panel_logs)
        
        return master_grid