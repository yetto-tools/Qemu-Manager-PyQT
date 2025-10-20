# qemu_adapters/ports.py
"""
Puertos (Interfaces) de la Arquitectura Hexagonal

UBICACIÓN: qemu_adapters/ports.py
PROPÓSITO: Definir interfaces que los adaptadores deben implementar
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional, Tuple

# ==================== IMPORTS LOCALES ====================
from qemu_domain.models import VirtualMachine


# ==================== PUERTO: EJECUTOR QEMU ====================

class QEMUExecutor(ABC):
    """
    Puerto para ejecutar comandos y máquinas virtuales QEMU
    
    Define el contrato que cualquier adaptador de ejecución QEMU debe cumplir.
    Permite cambiar la implementación sin afectar el resto de la aplicación.
    """
    
    @abstractmethod
    def execute(self, command: str) -> Tuple[int, str, str]:
        """
        Ejecuta un comando en shell
        
        Argumentos:
            command: Comando a ejecutar
        
        Retorna:
            tuple: (código_retorno, stdout, stderr)
        """
        pass
    
    @abstractmethod
    def start_vm(self, vm: VirtualMachine) -> bool:
        """
        Inicia una máquina virtual
        
        Argumentos:
            vm: Objeto VirtualMachine a iniciar
        
        Retorna:
            bool: True si se inició correctamente, False si falló
        """
        pass
    
    @abstractmethod
    def stop_vm(self, name: str) -> bool:
        """
        Detiene una máquina virtual
        
        Argumentos:
            name: Nombre de la VM a detener
        
        Retorna:
            bool: True si se detuvo correctamente
        """
        pass


# ==================== PUERTO: ADAPTADOR DE ALMACENAMIENTO ====================

class StorageAdapter(ABC):
    """
    Puerto para gestionar almacenamiento y discos virtuales
    
    Maneja operaciones con discos QEMU, conversiones de formato, etc.
    """
    
    @abstractmethod
    def create_disk(self, path: str, size_gb: float, format_type: str) -> bool:
        """
        Crea un nuevo disco virtual
        
        Argumentos:
            path: Ruta del archivo del disco
            size_gb: Tamaño en gigabytes
            format_type: Formato (qcow2, raw, vdi, vmdk)
        
        Retorna:
            bool: True si se creó correctamente
        """
        pass
    
    @abstractmethod
    def convert_disk(self, source: str, dest: str, format_type: str) -> bool:
        """
        Convierte un disco a otro formato
        
        Argumentos:
            source: Ruta del disco de origen
            dest: Ruta del disco de destino
            format_type: Formato destino
        
        Retorna:
            bool: True si se convirtió correctamente
        """
        pass
    
    @abstractmethod
    def delete_disk(self, path: str) -> bool:
        """
        Elimina un archivo de disco
        
        Argumentos:
            path: Ruta del disco a eliminar
        
        Retorna:
            bool: True si se eliminó correctamente
        """
        pass
    
    @abstractmethod
    def get_disk_info(self, path: str) -> Dict:
        """
        Obtiene información de un disco
        
        Argumentos:
            path: Ruta del disco
        
        Retorna:
            dict: Información del disco (formato, tamaño, etc)
        """
        pass


# ==================== PUERTO: PERSISTENCIA DE CONFIGURACIÓN ====================

class ConfigPersistence(ABC):
    """
    Puerto para persistencia de configuración
    
    Maneja guardado y carga de configuraciones en diferentes formatos.
    Permite cambiar de JSON a base de datos sin afectar la lógica.
    """
    
    @abstractmethod
    def save_config(self, key: str, data: Dict) -> None:
        """
        Guarda configuración
        
        Argumentos:
            key: Clave para identificar la configuración
            data: Diccionario de datos a guardar
        """
        pass
    
    @abstractmethod
    def load_config(self, key: str) -> Dict:
        """
        Carga configuración guardada
        
        Argumentos:
            key: Clave de la configuración
        
        Retorna:
            dict: Datos cargados o {} si no existe
        """
        pass
    
    @abstractmethod
    def list_configs(self) -> List[str]:
        """
        Lista todas las configuraciones disponibles
        
        Retorna:
            list: Lista de claves de configuración
        """
        pass


# ==================== PUERTO: MONITOR DEL SISTEMA ====================

class SystemMonitor(ABC):
    """
    Puerto para monitoreo del sistema
    
    Obtiene información de recursos del sistema.
    """
    
    @abstractmethod
    def get_cpu_usage(self) -> float:
        """
        Obtiene uso de CPU
        
        Retorna:
            float: Porcentaje de uso (0-100)
        """
        pass
    
    @abstractmethod
    def get_memory_usage(self) -> Dict:
        """
        Obtiene uso de memoria
        
        Retorna:
            dict: Información de memoria (total, usado, disponible)
        """
        pass
    
    @abstractmethod
    def get_disk_usage(self, path: str) -> Dict:
        """
        Obtiene uso de disco en una ruta
        
        Argumentos:
            path: Ruta a verificar
        
        Retorna:
            dict: Información de disco (total, usado, libre)
        """
        pass


# ==================== PUERTO: NOTIFICACIONES ====================

class NotificationService(ABC):
    """
    Puerto para servicios de notificación
    
    Permite enviar notificaciones a diferentes destinos.
    """
    
    @abstractmethod
    def send_notification(self, title: str, message: str, level: str = "info") -> bool:
        """
        Envía una notificación
        
        Argumentos:
            title: Título de la notificación
            message: Mensaje
            level: Nivel (info, warning, error, success)
        
        Retorna:
            bool: True si se envió correctamente
        """
        pass


# ==================== PUERTO: REGISTRO DE EVENTOS ====================

class EventLog(ABC):
    """
    Puerto para registro de eventos
    
    Registra eventos importantes de la aplicación.
    """
    
    @abstractmethod
    def log_event(self, event_type: str, description: str, data: Dict = None) -> None:
        """
        Registra un evento
        
        Argumentos:
            event_type: Tipo de evento (vm_started, vm_stopped, etc)
            description: Descripción del evento
            data: Datos adicionales (opcional)
        """
        pass
    
    @abstractmethod
    def get_events(self, limit: int = 100) -> List[Dict]:
        """
        Obtiene eventos registrados
        
        Argumentos:
            limit: Número máximo de eventos a obtener
        
        Retorna:
            list: Lista de eventos
        """
        pass