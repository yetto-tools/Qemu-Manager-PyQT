# ==================== qemu_application/service.py ====================

"""
Servicio de aplicación - Orquestación de casos de uso
"""

from typing import Optional, List

from qemu_domain.models import VirtualMachine, VMStatus, DiskFormat
from qemu_domain.use_cases import VMUseCase, DiskUseCase
from qemu_adapters.ports import QEMUExecutor, StorageAdapter


class QEMUApplicationService:
    """
    Servicio de aplicación que orquesta los casos de uso
    
    Coordina la interacción entre los casos de uso de dominio
    y los adaptadores de infraestructura.
    """
    
    def __init__(self, vm_use_case: VMUseCase, disk_use_case: DiskUseCase,
                 qemu_executor: QEMUExecutor, storage: StorageAdapter):
        """
        Constructor con inyección de dependencias
        
        Argumentos:
            vm_use_case: Caso de uso de VMs
            disk_use_case: Caso de uso de discos
            qemu_executor: Ejecutor QEMU
            storage: Adaptador de almacenamiento
        """
        self.vm_use_case = vm_use_case
        self.disk_use_case = disk_use_case
        self.qemu_executor = qemu_executor
        self.storage = storage
    
    # ==================== OPERACIONES CON VMs ====================
    
    def create_vm(self, name: str, disk: str, cpus: int = 2, 
                  ram: int = 1024, iso: Optional[str] = None, 
                  os: str = "Linux") -> Optional[VirtualMachine]:
        """
        Crea y persiste una nueva VM
        
        Argumentos:
            name: Nombre de la VM
            disk: Ruta del disco
            cpus: Número de núcleos
            ram: Memoria en MB
            iso: Ruta de ISO (opcional)
            os: Sistema operativo
        
        Retorna:
            VirtualMachine creada o None si falla
        """
        try:
            vm = self.vm_use_case.create_vm(
                name=name,
                disk=disk,
                iso=iso,
                cpus=cpus,
                ram=ram,
                os=os
            )
            return vm
        except Exception as e:
            print(f"Error creando VM: {e}")
            return None
    
    def get_all_vms(self) -> List[VirtualMachine]:
        """Obtiene todas las VMs"""
        try:
            return self.vm_use_case.get_all_vms()
        except Exception as e:
            print(f"Error obteniendo VMs: {e}")
            return []
    
    def get_vm(self, name: str) -> Optional[VirtualMachine]:
        """Obtiene una VM específica"""
        try:
            return self.vm_use_case.get_vm(name)
        except Exception as e:
            print(f"Error obteniendo VM: {e}")
            return None
    
    def start_vm(self, name: str) -> bool:
        """
        Inicia una VM
        
        Argumentos:
            name: Nombre de la VM
        
        Retorna:
            bool: True si se inició correctamente
        """
        try:
            vm = self.vm_use_case.get_vm(name)
            if not vm:
                return False
            
            # Iniciar VM
            if not self.qemu_executor.start_vm(vm):
                return False
            
            # Actualizar estado
            vm.status = VMStatus.RUNNING
            self.vm_use_case.update_vm(vm)
            return True
        except Exception as e:
            print(f"Error iniciando VM: {e}")
            return False
    
    def stop_vm(self, name: str) -> bool:
        """
        Detiene una VM
        
        Argumentos:
            name: Nombre de la VM
        
        Retorna:
            bool: True si se detuvo correctamente
        """
        try:
            # Detener proceso
            if not self.qemu_executor.stop_vm(name):
                return False
            
            # Actualizar estado
            vm = self.vm_use_case.get_vm(name)
            if vm:
                vm.status = VMStatus.STOPPED
                self.vm_use_case.update_vm(vm)
            
            return True
        except Exception as e:
            print(f"Error deteniendo VM: {e}")
            return False
    
    def delete_vm(self, name: str) -> bool:
        """
        Elimina una VM
        
        Argumentos:
            name: Nombre de la VM
        
        Retorna:
            bool: True si se eliminó correctamente
        """
        try:
            self.vm_use_case.delete_vm(name)
            return True
        except Exception as e:
            print(f"Error eliminando VM: {e}")
            return False
    
    def create_and_start_vm(self, name: str, disk: str, cpus: int, ram: int) -> bool:
        """
        Crea e inicia una VM
        
        Argumentos:
            name: Nombre de la VM
            disk: Ruta del disco
            cpus: Número de núcleos
            ram: Memoria en MB
        
        Retorna:
            bool: True si se creó e inició correctamente
        """
        try:
            vm = self.create_vm(name, disk, cpus, ram)
            if not vm:
                return False
            
            return self.start_vm(name)
        except Exception as e:
            print(f"Error creando e iniciando VM: {e}")
            return False
    
    def stop_vm_and_save(self, name: str) -> bool:
        """
        Detiene una VM y guarda su estado
        
        Argumentos:
            name: Nombre de la VM
        
        Retorna:
            bool: True si se completó correctamente
        """
        try:
            if not self.stop_vm(name):
                return False
            
            vm = self.vm_use_case.get_vm(name)
            if vm:
                vm.status = VMStatus.STOPPED
                self.vm_use_case.update_vm(vm)
            
            return True
        except Exception as e:
            print(f"Error deteniendo y guardando VM: {e}")
            return False
    
    # ==================== OPERACIONES CON DISCOS ====================
    
    def create_disk(self, name: str, path: str, size_gb: float, 
                   format_type: str = "qcow2") -> bool:
        """
        Crea un nuevo disco virtual
        
        Argumentos:
            name: Nombre del disco
            path: Ruta del archivo
            size_gb: Tamaño en GB
            format_type: Formato (qcow2, raw, vdi, vmdk)
        
        Retorna:
            bool: True si se creó correctamente
        """
        try:
            # Crear en almacenamiento
            if not self.storage.create_disk(path, size_gb, format_type):
                return False
            
            # Registrar en repositorio
            disk_format = DiskFormat(format_type)
            location = str(path.rsplit('/', 1)[0] if '/' in path else path.rsplit('\\', 1)[0])
            
            self.disk_use_case.create_disk(name, path, size_gb, disk_format, location)
            return True
        except Exception as e:
            print(f"Error creando disco: {e}")
            return False
    
    def get_all_disks(self):
        """Obtiene todos los discos"""
        try:
            return self.disk_use_case.get_all_disks()
        except Exception as e:
            print(f"Error obteniendo discos: {e}")
            return []
    
    def delete_disk(self, path: str) -> bool:
        """
        Elimina un disco
        
        Argumentos:
            path: Ruta del disco
        
        Retorna:
            bool: True si se eliminó correctamente
        """
        try:
            # Eliminar del almacenamiento
            if not self.storage.delete_disk(path):
                return False
            
            # Remover del repositorio
            self.disk_use_case.delete_disk(path)
            return True
        except Exception as e:
            print(f"Error eliminando disco: {e}")
            return False
    
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
        try:
            return self.storage.convert_disk(source, dest, format_type)
        except Exception as e:
            print(f"Error convirtiendo disco: {e}")
            return False
    
    def get_disk_info(self, path: str):
        """
        Obtiene información de un disco
        
        Argumentos:
            path: Ruta del disco
        
        Retorna:
            dict: Información del disco
        """
        try:
            return self.storage.get_disk_info(path)
        except Exception as e:
            print(f"Error obteniendo información del disco: {e}")
            return {}
    
    # ==================== OPERACIONES COMPUESTAS ====================
    
    def get_system_status(self) -> dict:
        """
        Obtiene estado general del sistema
        
        Retorna:
            dict: Estado de VMs, discos, etc
        """
        try:
            return {
                'vms_total': len(self.get_all_vms()),
                'disks_total': len(self.get_all_disks()),
                'vms_running': len([vm for vm in self.get_all_vms() if vm.status == VMStatus.RUNNING]),
                'timestamp': __import__('datetime').datetime.now().isoformat()
            }
        except Exception as e:
            print(f"Error obteniendo estado del sistema: {e}")
            return {}