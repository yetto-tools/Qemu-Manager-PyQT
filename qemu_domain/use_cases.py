"""
Casos de uso de la aplicación (Lógica de Negocio)

UBICACIÓN: qemu_domain/use_cases.py
PROPÓSITO: Implementar la lógica de negocio independiente del framework
"""

import sys
from typing import List, Optional

# ==================== IMPORTS LOCALES ====================
from qemu_domain.models import (
    VirtualMachine, VirtualDisk, DiskFormat, VMStatus, 
    Network, VideoConfig, AudioConfig, USBConfig
)
from qemu_domain.repositories import VMRepository, DiskRepository
from qemu_adapters.config_manager import get_config

# ==================== CASO DE USO: MÁQUINAS VIRTUALES ====================

class VMUseCase:
    """
    Caso de uso para gestión de máquinas virtuales
    
    Contiene toda la lógica de negocio relacionada con VMs.
    No depende de frameworks ni detalles de implementación.
    """
    
    def __init__(self, vm_repo: VMRepository):
        """
        Constructor con inyección de dependencias
        
        Argumentos:
            vm_repo: Repositorio de VMs (interfaz VMRepository)
        """
        self.vm_repo = vm_repo
    
    def create_vm(self, name: str, disk: str, iso: Optional[str] = None, 
                  cpus: int = 2, ram: int = 1024, os: str = "Linux",
                  vga: str = "qxl", boot_order: str = "Disco duro (para arrancar SO)") -> VirtualMachine:
        """
        Crea una nueva máquina virtual
        
        Argumentos:
            name: Nombre de la VM
            disk: Ruta del disco
            iso: Ruta de la imagen ISO (opcional)
            cpus: Número de núcleos CPU
            ram: Memoria RAM en MB
            os: Sistema operativo
            vga: Tipo de tarjeta gráfica (qxl, virtio, vmware, vga)
            boot_order: Orden de boot
        
        Retorna:
            VirtualMachine: La VM creada
        """
        vm = VirtualMachine(
            name=name,
            disk=disk,
            iso=iso,
            cpus=cpus,
            ram=ram,
            os=os,
            status=VMStatus.STOPPED
        )
        # Agregar atributos adicionales
        vm.vga = vga
        vm.boot_order = boot_order
        
        self.vm_repo.save(vm)
        return vm
    
    def get_all_vms(self) -> List[VirtualMachine]:
        """
        Obtiene todas las máquinas virtuales
        
        Retorna:
            List[VirtualMachine]: Lista de todas las VMs
        """
        return self.vm_repo.find_all()
    
    def get_vm(self, name: str) -> Optional[VirtualMachine]:
        """
        Obtiene una máquina virtual específica
        
        Argumentos:
            name: Nombre de la VM
        
        Retorna:
            VirtualMachine si existe, None en caso contrario
        """
        return self.vm_repo.find_by_name(name)
    
    def update_vm(self, vm: VirtualMachine) -> None:
        """
        Actualiza una máquina virtual
        
        Argumentos:
            vm: Objeto VirtualMachine con cambios
        """
        self.vm_repo.update(vm)
    
    def delete_vm(self, name: str) -> None:
        """
        Elimina una máquina virtual
        
        Argumentos:
            name: Nombre de la VM a eliminar
        """
        self.vm_repo.delete(name)
    
    def change_vm_status(self, name: str, status: VMStatus) -> Optional[VirtualMachine]:
        """
        Cambia el estado de una VM
        
        Argumentos:
            name: Nombre de la VM
            status: Nuevo estado (STOPPED, RUNNING, PAUSED)
        
        Retorna:
            VirtualMachine actualizada o None
        """
        vm = self.vm_repo.find_by_name(name)
        if vm:
            vm.status = status
            self.vm_repo.update(vm)
        return vm


# ==================== CASO DE USO: DISCOS VIRTUALES ====================

class DiskUseCase:
    """
    Caso de uso para gestión de discos virtuales
    
    Contiene toda la lógica de negocio relacionada con discos.
    """
    
    def __init__(self, disk_repo: DiskRepository):
        """
        Constructor con inyección de dependencias
        
        Argumentos:
            disk_repo: Repositorio de discos (interfaz DiskRepository)
        """
        self.disk_repo = disk_repo
    
    def create_disk(self, name: str, path: str, size_gb: float, 
                   format_type: DiskFormat, location: str) -> VirtualDisk:
        """
        Crea un nuevo disco virtual
        
        Argumentos:
            name: Nombre del disco
            path: Ruta del archivo del disco
            size_gb: Tamaño en GB
            format_type: Formato (QCOW2, RAW, VDI, VMDK)
            location: Ubicación del disco
        
        Retorna:
            VirtualDisk: El disco creado
        """
        disk = VirtualDisk(
            name=name,
            path=path,
            size_gb=size_gb,
            format=format_type,
            location=location
        )
        self.disk_repo.save(disk)
        return disk
    
    def get_all_disks(self) -> List[VirtualDisk]:
        """
        Obtiene todos los discos virtuales
        
        Retorna:
            List[VirtualDisk]: Lista de todos los discos
        """
        return self.disk_repo.find_all()
    
    def get_disk(self, path: str) -> Optional[VirtualDisk]:
        """
        Obtiene un disco específico por ruta
        
        Argumentos:
            path: Ruta del disco
        
        Retorna:
            VirtualDisk si existe, None en caso contrario
        """
        return self.disk_repo.find_by_path(path)
    
    def delete_disk(self, path: str) -> None:
        """
        Elimina un disco virtual
        
        Argumentos:
            path: Ruta del disco a eliminar
        """
        self.disk_repo.delete(path)
    
    def update_disk(self, disk: VirtualDisk) -> None:
        """
        Actualiza información de un disco
        
        Argumentos:
            disk: Objeto VirtualDisk con cambios
        """
        self.disk_repo.update(disk)


# ==================== CONSTRUCTOR DE COMANDOS QEMU ====================

class QEMUCommandBuilder:
    """
    Construye comandos QEMU basados en configuración
    
    Esta clase encapsula la lógica de construcción de líneas de comando
    para ejecutar máquinas virtuales con QEMU.
    """
    
    @staticmethod
    def _quote_path(path: str) -> str:
        """
        Agrega comillas a la ruta según el sistema operativo
        
        Argumentos:
            path: Ruta del archivo
        
        Retorna:
            str: Ruta entre comillas dobles
        """
        return f'"{path}"'
    
    @staticmethod
    def build_command(vm: VirtualMachine, video: Optional[VideoConfig] = None,
                     audio: Optional[AudioConfig] = None, 
                     usb: Optional[USBConfig] = None) -> str:
        """
        Construye comando QEMU completo
        
        Argumentos:
            vm: Configuración de la máquina virtual
            video: Configuración de video (opcional)
            audio: Configuración de audio (opcional)
            usb: Configuración USB (opcional)
        
        Retorna:
            str: Comando QEMU listo para ejecutar
        """
        config = get_config()

        cmd = "qemu-system-x86_64"
        
        # Nombre de la VM
        cmd += f" -name {vm.name}"
        
        # Memoria
        cmd += f" -m {vm.ram}"
        
        # CPU
        cmd += f" -smp cores={vm.cpus}"
        
        # ISO (si existe)
        if vm.iso:
            iso_quoted = QEMUCommandBuilder._quote_path(vm.iso)
            cmd += f" -cdrom {iso_quoted}"
        
        # Disco duro
        if vm.disk:
            disk_quoted = QEMUCommandBuilder._quote_path(vm.disk)
            cmd += f" -hda {disk_quoted}"
        
        # Orden de boot - Usar configuración de la VM
        boot_order = getattr(vm, 'boot_order', 'Disco duro (para arrancar SO)')
        if "Disco duro" in boot_order:
            cmd += " -boot order=cd,menu=on,splash-time=5000"
        else:
            cmd += " -boot order=dc,menu=on,splash-time=5000"

        # USB para entrada
        cmd += " -usb"
        cmd += " -device usb-kbd"
        cmd += " -device usb-mouse"

        # VGA - Usar configuración de la VM
        vga = getattr(vm, 'vga', 'qxl')
        cmd += f" -vga {vga}"

        # Display con captura de entrada mejorada
        cmd += " -display gtk,grab-on-hover=on"
        
        # Video (si se especifica)
        if video:
            if video.gl_acceleration:
                cmd += " -enable-kvm"
            
            if video.virgl:
                cmd += " -device virtio-gpu-gl"
        
        # Audio (si está habilitado)
        if audio and audio.enabled:
            cmd += f" -audiodev {audio.driver},id=audio0"
            cmd += f" -device {audio.model},audiodev=audio0"
        
        # Red
        cmd += " -net nic,model=virtio"
        cmd += " -net user"
        
        # USB (si se especifica)
        if usb:
            cmd += f" -device usb-ehci,id=ehci"
            for i in range(usb.ports):
                cmd += f" -device usb-port,bus=ehci.0,nr={i+1}"
        
        # Aceleración
        cmd += config.get_acceleration_flag()

        # Ejecutar en background
        cmd += " &"
        
        return cmd
    
    @staticmethod
    def build_minimal_command(vm: VirtualMachine) -> str:
        """
        Construye comando QEMU minimal
        
        Útil para máquinas virtuales simples.
        
        Argumentos:
            vm: Configuración de la máquina virtual
        
        Retorna:
            str: Comando QEMU minimal
        """
        cmd = "qemu-system-x86_64"
        cmd += f" -name {vm.name}"
        cmd += f" -m {vm.ram}"
        cmd += f" -smp cores={vm.cpus}"
        
        if vm.iso:
            iso_quoted = QEMUCommandBuilder._quote_path(vm.iso)
            cmd += f" -cdrom {iso_quoted}"
        
        if vm.disk:
            disk_quoted = QEMUCommandBuilder._quote_path(vm.disk)
            cmd += f" -hda {disk_quoted}"
        
        boot_order = getattr(vm, 'boot_order', 'Disco duro (para arrancar SO)')
        if "Disco duro" in boot_order:
            cmd += " -boot order=cd,menu=on,splash-time=5000"
        else:
            cmd += " -boot order=dc,menu=on,splash-time=5000"

        cmd += " -display gtk,grab-on-hover=on"
        cmd += " &"

        return cmd

    @staticmethod
    def build_kvm_command(vm: VirtualMachine) -> str:
        """
        Construye comando QEMU con aceleración KVM
        
        Requiere que KVM esté disponible en el sistema.
        
        Argumentos:
            vm: Configuración de la máquina virtual
        
        Retorna:
            str: Comando QEMU con KVM habilitado
        """
        cmd = "qemu-system-x86_64"
        cmd += f" -name {vm.name}"
        cmd += f" -m {vm.ram}"
        cmd += f" -smp cores={vm.cpus}"
        
        cmd += " -enable-kvm"
        cmd += " -cpu host"
        
        if vm.iso:
            iso_quoted = QEMUCommandBuilder._quote_path(vm.iso)
            cmd += f" -cdrom {iso_quoted}"
        
        if vm.disk:
            disk_quoted = QEMUCommandBuilder._quote_path(vm.disk)
            cmd += f" -hda {disk_quoted}"
        
        boot_order = getattr(vm, 'boot_order', 'Disco duro (para arrancar SO)')
        if "Disco duro" in boot_order:
            cmd += " -boot order=cd,menu=on,splash-time=5000"
        else:
            cmd += " -boot order=dc,menu=on,splash-time=5000"

        cmd += " -display gtk,grab-on-hover=on"
        cmd += " &"

        return cmd