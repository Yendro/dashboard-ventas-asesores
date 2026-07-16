import json
import uuid
import logging
from pathlib import Path
from typing import List

logger = logging.getLogger(__name__)

class TokenManager:
    def __init__(self, output_dir: Path):
        self.config_file = output_dir / "config.json"
        self.tokens = self._cargar_tokens()

    def _cargar_tokens(self) -> dict:
        if self.config_file.exists():
            with open(self.config_file, 'r', encoding='utf-8') as f:
                return json.load(f)
        return {}

    def actualizar_tokens(self, asesores: List[str]) -> bool:
        """
        Revisa la lista de asesores y asigna un UUID a los nuevos.
        Retorna True si hubo cambios, False si todo quedó igual.
        """
        nuevos_asignados = False
        for asesor in asesores:
            asesor_clean = str(asesor).strip()
            if asesor_clean not in self.tokens:
                nuevo_token = str(uuid.uuid4())
                self.tokens[asesor_clean] = nuevo_token
                logger.info(f"Nuevo token generado para: {asesor_clean}")
                nuevos_asignados = True
        
        if nuevos_asignados or not self.config_file.exists():
            self._guardar_tokens()
        else:
            logger.info("No se encontraron asesores nuevos. Tokens intactos.")
            
        return nuevos_asignados

    def _guardar_tokens(self):
        with open(self.config_file, 'w', encoding='utf-8') as f:
            json.dump(self.tokens, f, indent=4, ensure_ascii=False)
        logger.info(f"Tokens guardados exitosamente en {self.config_file.name}")