import json
import uuid
import logging
from pathlib import Path
from typing import List, Dict

logger = logging.getLogger(__name__)

class TokenManager:
    """
    Gestiona la lectura, creación y guardado de los tokens únicos (UUIDs)
    para cada asesor, los cuales actúan como contraseñas seguras para la Web App.
    """
    def __init__(self, output_dir: Path):
        self.config_file = output_dir / "config.json"
        self.tokens = self._cargar_tokens()

    def _cargar_tokens(self) -> dict:
        """Lee el JSON local de configuración si existe."""
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def actualizar_tokens(self, asesores: List[str]) -> Dict[str, str]:
        """
        Cruza la lista de asesores extraída de BigQuery con los tokens existentes.
        Si encuentra un asesor nuevo, le asigna un token.
        
        Retorna:
            Dict[str, str]: Un diccionario con { "NombreAsesor": "SuNuevoToken" }
                            Útil para notificaciones posteriores. (Si está vacío, no hubo cambios).
        """
        nuevos_asesores = {}
        
        for asesor in asesores:
            asesor_clean = str(asesor).strip()
            
            # Si el asesor no tiene token, se le genera uno nuevo
            if asesor_clean not in self.tokens:
                nuevo_token = str(uuid.uuid4())
                self.tokens[asesor_clean] = nuevo_token
                nuevos_asesores[asesor_clean] = nuevo_token
                
                logger.info(f"Nuevo token generado para: {asesor_clean}")
        
        # Solo sobreescribe el archivo local si hubo creaciones nuevas
        if nuevos_asesores or not self.config_file.exists():
            self._guardar_tokens()
        else:
            logger.info("No se encontraron asesores nuevos. Tokens intactos.")
            
        return nuevos_asesores

    def _guardar_tokens(self):
        """Guarda el diccionario maestro de tokens en formato JSON."""
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.tokens, f, indent=4, ensure_ascii=False)
        logger.info(f"Tokens guardados exitosamente en {self.config_file.name}")