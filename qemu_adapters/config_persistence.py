# ==================== qemu_adapters/config_persistence.py ====================

"""
Implementación de persistencia con JSON
"""

import json
from pathlib import Path
from typing import Dict, List

from qemu_adapters.ports import ConfigPersistence


class JSONConfigPersistence(ConfigPersistence):
    """Implementación de persistencia usando archivos JSON"""
    
    def __init__(self, config_dir: str = None):
        if config_dir is None:
            config_dir = str(Path.home() / ".qemu_manager")
        self.config_dir = Path(config_dir)
        self.config_dir.mkdir(parents=True, exist_ok=True)
    
    def save_config(self, key: str, data: Dict) -> None:
        """Guarda configuración en JSON"""
        config_file = self.config_dir / f"{key}.json"
        with open(config_file, 'w') as f:
            json.dump(data, f, indent=2)
    
    def load_config(self, key: str) -> Dict:
        """Carga configuración desde JSON"""
        config_file = self.config_dir / f"{key}.json"
        if config_file.exists():
            with open(config_file, 'r') as f:
                return json.load(f)
        return {}
    
    def list_configs(self) -> List[str]:
        """Lista todas las configuraciones"""
        return [f.stem for f in self.config_dir.glob("*.json")]