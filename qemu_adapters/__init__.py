
# qemu_adapters/__init__.py
"""Paquete de adaptadores"""

from .qemu_executor import QEMUExecutorImpl
from .storage_adapter import StorageAdapterImpl
from .config_persistence import JSONConfigPersistence
from .repositories import JSONVMRepository, JSONDiskRepository

__all__ = [
    'QEMUExecutorImpl',
    'StorageAdapterImpl',
    'JSONConfigPersistence',
    'JSONVMRepository',
    'JSONDiskRepository',
]
