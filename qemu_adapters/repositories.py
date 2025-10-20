# ==================== qemu_adapters/repositories.py ====================

"""
Implementación de repositorios con JSON
"""

import json
from typing import Dict, List, Optional
from pathlib import Path

from qemu_adapters.ports import ConfigPersistence
from qemu_domain.models import VirtualMachine, VirtualDisk, DiskFormat, VMStatus
from qemu_domain.repositories import VMRepository, DiskRepository


class JSONVMRepository(VMRepository):
    """Repositorio de VMs con persistencia JSON"""
    
    def __init__(self, persistence: ConfigPersistence):
        self.persistence = persistence
    
    def save(self, vm: VirtualMachine) -> None:
        """Guarda una VM"""
        vms = self._load_all()
        vms[vm.name] = {
            "name": vm.name,
            "disk": vm.disk,
            "iso": vm.iso,
            "cpus": vm.cpus,
            "ram": vm.ram,
            "os": vm.os,
            "status": vm.status.value,
            "auto_detected": vm.auto_detected
        }
        self.persistence.save_config("vms", vms)
    
    def find_by_name(self, name: str) -> Optional[VirtualMachine]:
        """Busca VM por nombre"""
        vms = self._load_all()
        if name in vms:
            data = vms[name]
            return VirtualMachine(
                name=data["name"],
                disk=data["disk"],
                iso=data.get("iso"),
                cpus=data.get("cpus", 2),
                ram=data.get("ram", 1024),
                os=data.get("os", "Linux"),
                status=VMStatus(data.get("status", "stopped")),
                auto_detected=data.get("auto_detected", False)
            )
        return None
    
    def find_all(self) -> List[VirtualMachine]:
        """Obtiene todas las VMs"""
        vms = self._load_all()
        result = []
        for data in vms.values():
            vm = VirtualMachine(
                name=data["name"],
                disk=data["disk"],
                iso=data.get("iso"),
                cpus=data.get("cpus", 2),
                ram=data.get("ram", 1024),
                os=data.get("os", "Linux"),
                status=VMStatus(data.get("status", "stopped")),
                auto_detected=data.get("auto_detected", False)
            )
            result.append(vm)
        return result
    
    def delete(self, name: str) -> None:
        """Elimina una VM"""
        vms = self._load_all()
        if name in vms:
            del vms[name]
            self.persistence.save_config("vms", vms)
    
    def _load_all(self) -> Dict:
        """Carga todas las VMs"""
        return self.persistence.load_config("vms") or {}


class JSONDiskRepository(DiskRepository):
    """Repositorio de discos con persistencia JSON"""
    
    def __init__(self, persistence: ConfigPersistence):
        self.persistence = persistence
    
    def save(self, disk: VirtualDisk) -> None:
        """Guarda un disco"""
        disks = self._load_all()
        disks[disk.path] = {
            "name": disk.name,
            "path": disk.path,
            "size_gb": disk.size_gb,
            "format": disk.format.value,
            "location": disk.location
        }
        self.persistence.save_config("disks", disks)
    
    def find_all(self) -> List[VirtualDisk]:
        """Obtiene todos los discos"""
        disks = self._load_all()
        result = []
        for data in disks.values():
            disk = VirtualDisk(
                name=data["name"],
                path=data["path"],
                size_gb=data["size_gb"],
                format=DiskFormat(data["format"]),
                location=data["location"]
            )
            result.append(disk)
        return result
    
    def delete(self, path: str) -> None:
        """Elimina un disco"""
        disks = self._load_all()
        if path in disks:
            del disks[path]
            self.persistence.save_config("disks", disks)
    
    def find_by_path(self, path: str) -> Optional[VirtualDisk]:
        """Busca disco por ruta"""
        disks = self._load_all()
        if path in disks:
            data = disks[path]
            return VirtualDisk(
                name=data["name"],
                path=data["path"],
                size_gb=data["size_gb"],
                format=DiskFormat(data["format"]),
                location=data["location"]
            )
        return None
    
    def _load_all(self) -> Dict:
        """Carga todos los discos"""
        return self.persistence.load_config("disks") or {}