"""
Implementación del adaptador de almacenamiento - CORREGIDO PARA WINDOWS
"""

import subprocess
import os
import sys
from typing import Dict
from pathlib import Path
import shutil

from qemu_adapters.ports import StorageAdapter


class StorageAdapterImpl(StorageAdapter):
    """Implementación concreta del adaptador de almacenamiento"""
    
    def __init__(self):
        """Inicializa el adaptador"""
        self.is_windows = sys.platform == 'win32'
        self.qemu_img_path = self._find_qemu_img()
    
    def _find_qemu_img(self) -> str:
        """Busca qemu-img en el sistema"""
        qemu_img = shutil.which('qemu-img')
        if qemu_img:
            print(f"[OK] qemu-img encontrado en: {qemu_img}")
            return qemu_img
        else:
            print("[WARN] qemu-img NO encontrado en PATH")
            return "qemu-img"  # Intenta de todos modos
    
    def create_disk(self, path: str, size_gb: float, format_type: str) -> bool:
        """Crea un nuevo disco virtual"""
        try:
            # Asegurar que la carpeta existe
            disk_path = Path(path)
            disk_path.parent.mkdir(parents=True, exist_ok=True)
            
            # Verificar que no existe ya
            if disk_path.exists():
                print(f"[WARN] Archivo ya existe: {path}")
                return False
            
            # Usar comillas dobles en Windows (mejor para rutas con espacios)
            if self.is_windows:
                cmd = f'"{self.qemu_img_path}" create -f {format_type} "{path}" {size_gb}G'
            else:
                cmd = f"{self.qemu_img_path} create -f {format_type} '{path}' {size_gb}G"
            
            print(f"[DEBUG] Ejecutando: {cmd}")
            print(f"[DEBUG] Ruta absoluta: {disk_path.absolute()}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=60,
                cwd=str(disk_path.parent)  # Ejecuta desde la carpeta del disco
            )
            
            if result.returncode == 0:
                # Verificar que el archivo se creó
                if disk_path.exists():
                    size_mb = disk_path.stat().st_size / (1024 * 1024)
                    print(f"[OK] Disco creado: {path}")
                    print(f"[OK] Tamaño: {size_mb:.2f} MB")
                    return True
                else:
                    print(f"[ERROR] Comando retornó 0 pero archivo NO existe: {path}")
                    return False
            else:
                print(f"[ERROR] Codigo retorno: {result.returncode}")
                print(f"[ERROR] stdout: {result.stdout}")
                print(f"[ERROR] stderr: {result.stderr}")
                return False
                
        except subprocess.TimeoutExpired:
            print("[ERROR] Timeout - operacion demorada")
            return False
        except Exception as e:
            print(f"[ERROR] {type(e).__name__}: {e}")
            return False
    
    def convert_disk(self, source: str, dest: str, format_type: str) -> bool:
        """Convierte formato de disco"""
        try:
            source_path = Path(source)
            dest_path = Path(dest)
            
            if not source_path.exists():
                print(f"[ERROR] Archivo fuente no existe: {source}")
                return False
            
            dest_path.parent.mkdir(parents=True, exist_ok=True)
            
            if self.is_windows:
                cmd = f'"{self.qemu_img_path}" convert -f auto -O {format_type} "{source}" "{dest}"'
            else:
                cmd = f"{self.qemu_img_path} convert -f auto -O {format_type} '{source}' '{dest}'"
            
            print(f"[DEBUG] Ejecutando: {cmd}")
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=300
            )
            
            if result.returncode == 0:
                print(f"[OK] Disco convertido: {dest}")
                return True
            else:
                print(f"[ERROR] {result.stderr}")
                return False
                
        except Exception as e:
            print(f"[ERROR] Error convirtiendo disco: {e}")
            return False
    
    def delete_disk(self, path: str) -> bool:
        """Elimina un disco"""
        try:
            disk_path = Path(path)
            if disk_path.exists():
                disk_path.unlink()
                print(f"[OK] Disco eliminado: {path}")
                return True
            else:
                print(f"[WARN] Archivo no existe: {path}")
                return False
        except Exception as e:
            print(f"[ERROR] Error eliminando disco: {e}")
            return False
    
    def get_disk_info(self, path: str) -> Dict:
        """Obtiene información del disco"""
        try:
            disk_path = Path(path)
            if not disk_path.exists():
                return {"error": f"Archivo no existe: {path}"}
            
            if self.is_windows:
                cmd = f'"{self.qemu_img_path}" info "{path}"'
            else:
                cmd = f"{self.qemu_img_path} info '{path}'"
            
            result = subprocess.run(
                cmd,
                shell=True,
                capture_output=True,
                text=True,
                timeout=10
            )
            
            if result.returncode == 0:
                return {"info": result.stdout, "error": ""}
            else:
                return {"info": "", "error": result.stderr}
                
        except Exception as e:
            return {"error": str(e)}