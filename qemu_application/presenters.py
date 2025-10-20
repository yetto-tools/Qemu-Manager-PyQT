# ==================== qemu_application/presenters.py ====================

"""
Presentadores para adaptar datos del dominio a la UI
"""

from typing import Any, Protocol, List
from qemu_domain.models import VirtualMachine, VirtualDisk


class VMPresenter(Protocol):
    """Interfaz para presentador de máquinas virtuales"""
    
    def present_vms(self, vms: List[VirtualMachine]) -> None:
        """Presenta lista de VMs"""
        ...
    
    def present_vm(self, vm: VirtualMachine) -> None:
        """Presenta VM individual"""
        ...
    
    def present_error(self, error: str) -> None:
        """Presenta error"""
        ...
    
    def present_success(self, message: str) -> None:
        """Presenta mensaje de éxito"""
        ...


class DiskPresenter(Protocol):
    """Interfaz para presentador de discos"""
    
    def present_disks(self, disks: List[VirtualDisk]) -> None:
        """Presenta lista de discos"""
        ...
    
    def present_disk_info(self, disk: VirtualDisk) -> None:
        """Presenta información del disco"""
        ...
    
    def present_success(self, message: str) -> None:
        """Presenta mensaje de éxito"""
        ...
    
    def present_error(self, error: str) -> None:
        """Presenta error"""
        ...