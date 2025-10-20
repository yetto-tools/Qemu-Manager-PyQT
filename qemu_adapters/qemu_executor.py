# ==================== qemu_adapters/qemu_executor.py ====================

"""
Implementación del adaptador QEMU Executor
"""

import subprocess
from typing import Tuple, Optional
from pathlib import Path

from qemu_adapters.ports import QEMUExecutor
from qemu_domain.models import VirtualMachine


class QEMUExecutorImpl(QEMUExecutor):
    """Implementación concreta del ejecutor QEMU"""
    
    def __init__(self):
        self.running_processes = {}
    
    def execute(self, command: str, timeout: int = 30) -> Tuple[int, str, str]:
        """Ejecuta comando en shell"""
        try:
            result = subprocess.run(
                command,
                shell=True,
                capture_output=True,
                text=True,
                timeout=timeout
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return -1, "", "Timeout"
        except Exception as e:
            return -1, "", str(e)
    
    def start_vm(self, vm: VirtualMachine) -> bool:
        """Inicia una máquina virtual"""
        try:
            from qemu_domain.use_cases import QEMUCommandBuilder
            builder = QEMUCommandBuilder()
            command = builder.build_command(vm)
            
            process = subprocess.Popen(command, shell=True)
            self.running_processes[vm.name] = process
            return True
        except Exception as e:
            print(f"Error iniciando VM: {e}")
            return False
    
    def stop_vm(self, name: str) -> bool:
        """Detiene una máquina virtual"""
        if name in self.running_processes:
            try:
                self.running_processes[name].terminate()
                self.running_processes[name].wait(timeout=5)
                del self.running_processes[name]
                return True
            except Exception as e:
                print(f"Error deteniendo VM: {e}")
                return False
        return False