# qemu_application/__init__.py
"""
Paquete de aplicación - Capa de servicios
"""

from .service import QEMUApplicationService
from .presenters import VMPresenter, DiskPresenter

__all__ = [
    'QEMUApplicationService',
    'VMPresenter',
    'DiskPresenter',
]

__version__ = '0.1.0'