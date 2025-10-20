"""
Paquete de diálogos para QEMU Manager
"""

from .disk_manager_dialog import DiskManagerDialog
from .network_dialog import NetworkDialog
from .video_dialog import VideoDialog
from .peripherals_dialog import PeripheralsDialog
from .search_dialog import SearchDialog
from .about_dialog import AboutDialog
from .settings_dialog import SettingsDialog

__all__ = [
    'DiskManagerDialog',
    'NetworkDialog',
    'VideoDialog',
    'PeripheralsDialog',
    'SearchDialog',
    'AboutDialog',
    'SettingsDialog',
]