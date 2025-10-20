# qemu_domain/repositories.py
"""
Interfaces de repositorios (Puertos)

UBICACIÓN: qemu_domain/repositories.py
PROPÓSITO: Definir contratos para acceso a datos
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Optional

# ==================== IMPORTS LOCALES ====================
from qemu_domain.models import VirtualMachine, VirtualDisk, DiskFormat


# ==================== REPOSITORIO DE MÁQUINAS VIRTUALES ====================

class VMRepository(ABC):
    """
    Interfaz para repositorio de máquinas virtuales
    
    Define el contrato que todo repositorio de VMs debe cumplir.
    Implementa el patrón Repository.
    """
    
    @abstractmethod
    def save(self, vm: VirtualMachine) -> None:
        """
        Guarda una máquina virtual
        
        Argumentos:
            vm: Objeto VirtualMachine a guardar
        """
        pass
    
    @abstractmethod
    def find_by_name(self, name: str) -> Optional[VirtualMachine]:
        """
        Busca una máquina virtual por nombre
        
        Argumentos:
            name: Nombre de la VM
        
        Retorna:
            VirtualMachine si existe, None si no
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[VirtualMachine]:
        """
        Obtiene todas las máquinas virtuales
        
        Retorna:
            Lista de VirtualMachine
        """
        pass
    
    @abstractmethod
    def delete(self, name: str) -> None:
        """
        Elimina una máquina virtual
        
        Argumentos:
            name: Nombre de la VM a eliminar
        """
        pass


# ==================== REPOSITORIO DE DISCOS ====================

class DiskRepository(ABC):
    """
    Interfaz para repositorio de discos virtuales
    
    Define el contrato que todo repositorio de discos debe cumplir.
    Implementa el patrón Repository.
    """
    
    @abstractmethod
    def save(self, disk: VirtualDisk) -> None:
        """
        Guarda un disco virtual
        
        Argumentos:
            disk: Objeto VirtualDisk a guardar
        """
        pass
    
    @abstractmethod
    def find_all(self) -> List[VirtualDisk]:
        """
        Obtiene todos los discos virtuales
        
        Retorna:
            Lista de VirtualDisk
        """
        pass
    
    @abstractmethod
    def delete(self, path: str) -> None:
        """
        Elimina un disco virtual
        
        Argumentos:
            path: Ruta del disco a eliminar
        """
        pass
    
    @abstractmethod
    def find_by_path(self, path: str) -> Optional[VirtualDisk]:
        """
        Busca un disco por ruta
        
        Argumentos:
            path: Ruta del disco
        
        Retorna:
            VirtualDisk si existe, None si no
        """
        pass


# ==================== REPOSITORIO DE REDES (FUTURO) ====================

class NetworkRepository(ABC):
    """
    Interfaz para repositorio de redes virtuales
    
    Reservado para futuras expansiones
    """
    
    @abstractmethod
    def save(self, network) -> None:
        """Guarda una red virtual"""
        pass
    
    @abstractmethod
    def find_all(self) -> List:
        """Obtiene todas las redes"""
        pass
    
    @abstractmethod
    def delete(self, name: str) -> None:
        """Elimina una red"""
        pass


# ==================== REPOSITORIO DE SNAPSHOTS (FUTURO) ====================

class SnapshotRepository(ABC):
    """
    Interfaz para repositorio de snapshots
    
    Reservado para futuras expansiones
    """
    
    @abstractmethod
    def save(self, snapshot) -> None:
        """Guarda un snapshot"""
        pass
    
    @abstractmethod
    def find_by_vm(self, vm_name: str) -> List:
        """Obtiene snapshots de una VM"""
        pass
    
    @abstractmethod
    def delete(self, snapshot_id: str) -> None:
        """Elimina un snapshot"""
        pass