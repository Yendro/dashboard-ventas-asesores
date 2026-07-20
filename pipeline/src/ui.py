from rich.layout import Layout
from rich.table import Table
from rich.panel import Panel
from rich.text import Text
from rich.console import Console

console = Console()

class PipelineUI:
    """
    Clase encargada de construir y actualizar la interfaz gráfica en la terminal
    utilizando la librería 'rich'.
    """
    def __init__(self):
        # Definimos los módulos estáticos de la pipeline.
        # Esto sirve como el "esqueleto" de la tabla izquierda.
        self.tasks = [
            {"id": "01", "mod": "bigquery_client.py", "status": "[dim]WAIT[/]"},
            {"id": "02", "mod": "token_manager.py", "status": "[dim]WAIT[/]"},
            {"id": "03", "mod": "drive_client.py", "status": "[dim]WAIT[/]"}
        ]
        
        # Lista para almacenar el historial de mensajes (logs) en tiempo real.
        self.logs = []

    def update_task(self, idx: int, status: str):
        """ Actualiza el estado visual de un módulo en la tabla. """
        self.tasks[idx]["status"] = status

    def log(self, message: str, style="white"):
        """ Agrega un nuevo mensaje al panel de logs de la derecha. """
        self.logs.append(f"[{style}]{message}[/]")
        if len(self.logs) > 12:  # Limite de mensajes
            self.logs.pop(0)

    def get_renderable(self):
        """
        Construye el 'Layout' maestro que divide la pantalla en dos columnas.
        Este método es llamado continuamente por Live() para refrescar la pantalla.
        """
        # --- 1. Tabla de Tareas (Panel Izquierdo) ---
        table = Table(box=None, expand=True)
        table.add_column("id", style="bold yellow", width=4)
        table.add_column("module", style="bold white")
        table.add_column("status", justify="right", width=10)
        
        for task in self.tasks:
            table.add_row(task["id"], task["mod"], task["status"])
            
        # Envolvemos la tabla en un panel con bordes cyan
        panel_table = Panel(table, title="[bold cyan]Pipeline status[/]", border_style="cyan", height=16)

        # --- 2. Historial de Logs (Panel Derecho) ---
        log_text = Text.from_markup("\n".join(self.logs))
        
        # Envolvemos los textos en un panel.
        panel_logs = Panel(log_text, title="[bold cyan]Execution Logs[/]", border_style="cyan", height=16)

        # --- 3. Unión de Paneles ---
        layout = Layout()
        layout.split_row(
            Layout(panel_table, name="left", ratio=1),
            Layout(panel_logs, name="right", ratio=2)
        )
        
        return layout