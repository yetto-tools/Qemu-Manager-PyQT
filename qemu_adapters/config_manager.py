"""
Gestor de configuración global de la aplicación
Guarda y carga preferencias del usuario
"""

import json
import sys
from pathlib import Path


class ConfigManager:
    """Gestiona la configuración global de QEMU Manager"""
    
    # Ruta del archivo de configuración
    CONFIG_DIR = Path.home() / ".qemu_manager"
    CONFIG_FILE = CONFIG_DIR / "settings.json"
    
    # Configuración por defecto
    DEFAULT_CONFIG = {
        "acceleration": {
            "enabled": True,
            "type": "whpx" if sys.platform == "win32" else "kvm",
            "description": "Tipo de aceleración de hardware"
        },
        "vm_defaults": {
            "cpus": 2,
            "ram": 1024,
            "vga": "qxl",
            "description": "Valores por defecto para nuevas VMs"
        },
        "ui": {
            "theme": "light",
            "window_geometry": None,
            "description": "Configuración de interfaz"
        },
        "paths": {
            "iso_dir": str(Path.home() / "Downloads"),
            "disk_dir": str(Path.home() / "VirtualMachines"),
            "description": "Directorios por defecto"
        }
    }
    
    def __init__(self):
        """Inicializa el gestor de configuración"""
        self.config = self.load_config()
    
    def load_config(self) -> dict:
        """Carga la configuración desde archivo o crea una nueva"""
        # Crear directorio si no existe
        self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        
        # Si el archivo existe, cargar
        if self.CONFIG_FILE.exists():
            try:
                with open(self.CONFIG_FILE, 'r', encoding='utf-8') as f:
                    config = json.load(f)
                    # Fusionar con defaults para nuevas opciones
                    return self._merge_defaults(config)
            except Exception as e:
                print(f"[WARN] Error cargando configuración: {e}")
                return self.DEFAULT_CONFIG.copy()
        
        # Crear nueva configuración por defecto
        self.save_config(self.DEFAULT_CONFIG)
        return self.DEFAULT_CONFIG.copy()
    
    def _merge_defaults(self, config: dict) -> dict:
        """Fusiona configuración existente con defaults"""
        result = self.DEFAULT_CONFIG.copy()
        for key in result:
            if key in config:
                if isinstance(result[key], dict) and isinstance(config[key], dict):
                    result[key].update(config[key])
                else:
                    result[key] = config[key]
        return result
    
    def save_config(self, config: dict = None) -> bool:
        """Guarda la configuración en archivo"""
        try:
            if config is None:
                config = self.config
            
            self.CONFIG_DIR.mkdir(parents=True, exist_ok=True)
            
            with open(self.CONFIG_FILE, 'w', encoding='utf-8') as f:
                json.dump(config, f, indent=2, ensure_ascii=False)
            
            self.config = config
            return True
        except Exception as e:
            print(f"[ERROR] No se pudo guardar configuración: {e}")
            return False
    
    # ==================== ACELERACIÓN ====================
    
    def get_acceleration_type(self) -> str:
        """Obtiene el tipo de aceleración configurado"""
        return self.config.get("acceleration", {}).get("type", "none")
    
    def set_acceleration_type(self, accel_type: str) -> bool:
        """Establece el tipo de aceleración"""
        valid_types = ["none", "kvm", "whpx", "hax", "tcg"]
        
        if accel_type not in valid_types:
            print(f"[ERROR] Tipo de aceleración inválido: {accel_type}")
            return False
        
        self.config["acceleration"]["type"] = accel_type
        self.config["acceleration"]["enabled"] = accel_type != "none"
        return self.save_config()
    
    def is_acceleration_enabled(self) -> bool:
        """Verifica si la aceleración está habilitada"""
        return self.config.get("acceleration", {}).get("enabled", False)
    
    def get_acceleration_flag(self) -> str:
        """Retorna el flag de aceleración para QEMU"""
        accel_type = self.get_acceleration_type()
        
        if accel_type == "none":
            return ""
        elif accel_type == "kvm":
            return " -enable-kvm"
        elif accel_type == "whpx":
            return " -accel whpx"
        elif accel_type == "hax":
            return " -accel hax"
        else:
            return ""
    
    # ==================== VALORES POR DEFECTO ====================
    
    def get_vm_defaults(self) -> dict:
        """Obtiene los valores por defecto de VMs"""
        return self.config.get("vm_defaults", {})
    
    def set_vm_defaults(self, defaults: dict) -> bool:
        """Establece los valores por defecto de VMs"""
        self.config["vm_defaults"].update(defaults)
        return self.save_config()
    
    # ==================== DIRECTORIOS ====================
    
    def get_iso_dir(self) -> str:
        """Obtiene el directorio de ISOs"""
        return self.config.get("paths", {}).get("iso_dir", str(Path.home() / "Downloads"))
    
    def set_iso_dir(self, path: str) -> bool:
        """Establece el directorio de ISOs"""
        self.config["paths"]["iso_dir"] = path
        return self.save_config()
    
    def get_disk_dir(self) -> str:
        """Obtiene el directorio de discos"""
        return self.config.get("paths", {}).get("disk_dir", str(Path.home() / "VirtualMachines"))
    
    def set_disk_dir(self, path: str) -> bool:
        """Establece el directorio de discos"""
        self.config["paths"]["disk_dir"] = path
        return self.save_config()
    
    # ==================== UI ====================
    
    def get_theme(self) -> str:
        """Obtiene el tema de UI"""
        return self.config.get("ui", {}).get("theme", "light")
    
    def set_theme(self, theme: str) -> bool:
        """Establece el tema de UI"""
        if theme not in ["light", "dark"]:
            return False
        self.config["ui"]["theme"] = theme
        return self.save_config()
    
    def print_config(self):
        """Imprime la configuración actual (sin 'description')"""
        display_config = {}
        for key, value in self.config.items():
            if isinstance(value, dict):
                display_config[key] = {k: v for k, v in value.items() if k != "description"}
            else:
                display_config[key] = value
        
        print("\n=== CONFIGURACIÓN ACTUAL ===")
        print(json.dumps(display_config, indent=2, ensure_ascii=False))
        print("=" * 30 + "\n")


# Instancia global
_config_manager = None

def get_config() -> ConfigManager:
    """Obtiene la instancia global del ConfigManager"""
    global _config_manager
    if _config_manager is None:
        _config_manager = ConfigManager()
    return _config_manager