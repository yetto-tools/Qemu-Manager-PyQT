# ==================== config.py ====================
# NIVEL: ROOT (Mismo nivel que main.py)
# UBICACIÓN: qemu-manager/config.py

"""
config.py - Configuración centralizada de la aplicación

Este archivo está en el NIVEL RAÍZ del proyecto, accesible desde
cualquier módulo usando: from config import ...
"""

import os
import logging
from pathlib import Path
from enum import Enum

# ==================== DIRECTORIOS ====================

# Directorio raíz del proyecto
PROJECT_ROOT = Path(__file__).parent.absolute()

# Directorios de usuario
CONFIG_DIR = Path.home() / ".qemu_manager"
LOGS_DIR = CONFIG_DIR / "logs"
CACHE_DIR = CONFIG_DIR / "cache"
BACKUP_DIR = CONFIG_DIR / "backups"
TEMPLATES_DIR = PROJECT_ROOT / "templates"

# Crear directorios si no existen
CONFIG_DIR.mkdir(parents=True, exist_ok=True)
LOGS_DIR.mkdir(parents=True, exist_ok=True)
CACHE_DIR.mkdir(parents=True, exist_ok=True)
BACKUP_DIR.mkdir(parents=True, exist_ok=True)

# ==================== ARCHIVOS DE CONFIGURACIÓN ====================

# Archivos de datos
VMS_CONFIG_FILE = CONFIG_DIR / "vms.json"
DISKS_CONFIG_FILE = CONFIG_DIR / "disks.json"
NETWORKS_CONFIG_FILE = CONFIG_DIR / "networks.json"
SETTINGS_CONFIG_FILE = CONFIG_DIR / "settings.json"

# Archivos de log
MAIN_LOG_FILE = LOGS_DIR / "qemu_manager.log"
ERROR_LOG_FILE = LOGS_DIR / "errors.log"
DEBUG_LOG_FILE = LOGS_DIR / "debug.log"

# ==================== CONFIGURACIÓN DE QEMU ====================

# Binarios QEMU
QEMU_BINARY = "qemu-system-x86_64"
QEMU_IMG_BINARY = "qemu-img"
QEMU_IO_BINARY = "qemu-io"

# Directorios de búsqueda de VMs
VM_SEARCH_PATHS = [
    "/var/lib/libvirt/images",
    "/var/lib/kvm/images",
    os.path.expanduser("~/VirtualMachines"),
    os.path.expanduser("~/QEMU"),
    os.path.expanduser("~/.qemu"),
    "/opt/qemu",
    "/usr/share/qemu",
]

# ==================== CONFIGURACIÓN DE ALMACENAMIENTO ====================

# Formatos de disco soportados
class DiskFormat(Enum):
    QCOW2 = "qcow2"
    RAW = "raw"
    VDI = "vdi"
    VMDK = "vmdk"
    VHDX = "vhdx"
    QED = "qed"

DISK_FORMATS = [fmt.value for fmt in DiskFormat]
DISK_FORMATS_DISPLAY = {
    "qcow2": "QCOW2 (Recomendado)",
    "raw": "RAW (Rendimiento)",
    "vdi": "VirtualBox VDI",
    "vmdk": "VMware VMDK",
    "vhdx": "Hyper-V VHDX"
}

# Tamaños preconfigurados de disco
DISK_PRESETS = {
    "Linux Mínimo": {"size": 10, "format": "qcow2"},
    "Linux Estándar": {"size": 20, "format": "qcow2"},
    "Linux Grande": {"size": 50, "format": "qcow2"},
    "Windows 10": {"size": 50, "format": "qcow2"},
    "Windows Server": {"size": 100, "format": "qcow2"},
    "Servidor DB": {"size": 200, "format": "qcow2"},
}

# ==================== CONFIGURACIÓN DE HARDWARE ====================

# CPU
CPU_MIN = 1
CPU_MAX = 16
CPU_DEFAULT = 2

# RAM (en MB)
RAM_MIN = 256
RAM_MAX = 131072  # 128 GB
RAM_DEFAULT = 1024
RAM_PRESETS = {
    "Mínima": 256,
    "Baja": 512,
    "Estándar": 1024,
    "Media": 2048,
    "Alta": 4096,
    "Muy Alta": 8192,
}

# ==================== CONFIGURACIÓN DE VIDEO ====================

# Tipos de tarjetas gráficas
VGA_TYPES = ["qxl", "virtio", "vmware", "vga", "cirrus", "std", "none"]
VGA_TYPES_DISPLAY = {
    "qxl": "QXL (SPICE)",
    "virtio": "Virtio (Recomendado)",
    "vmware": "VMware SVGA",
    "vga": "VGA Estándar",
    "cirrus": "Cirrus (Legacy)",
    "std": "Estándar",
    "none": "Sin video"
}

# Resoluciones de video
VIDEO_RESOLUTIONS = [
    "1024x768",
    "1280x1024",
    "1366x768",
    "1600x1200",
    "1920x1080",
    "2560x1440",
    "3840x2160",
    "4096x2304",
    "5120x2880",
]

# VRAM
VRAM_MIN = 4
VRAM_MAX = 512
VRAM_DEFAULT = 64
VRAM_PRESETS = {
    "Mínima": 4,
    "Baja": 16,
    "Estándar": 64,
    "Media": 128,
    "Alta": 256,
}

# Profundidad de color
COLOR_DEPTHS = [8, 16, 24, 32]
COLOR_DEPTHS_DISPLAY = {
    8: "8 bits (256 colores)",
    16: "16 bits (65K colores)",
    24: "24 bits (16M colores)",
    32: "32 bits (32M colores + alfa)",
}

# ==================== CONFIGURACIÓN DE RED ====================

# Tipos de red
class NetworkType(Enum):
    USER = "user"
    BRIDGE = "bridge"
    TAP = "tap"
    VDE = "vde"
    SOCKET = "socket"

NETWORK_TYPES = [nt.value for nt in NetworkType]
NETWORK_TYPES_DISPLAY = {
    "user": "Usuario (NAT)",
    "bridge": "Bridge",
    "tap": "TAP",
    "vde": "VDE",
    "socket": "Socket"
}

# Modelos de interfaz de red
NETWORK_MODELS = ["virtio", "e1000", "rtl8139", "i82559er", "pcnet", "ne2k_pci"]
NETWORK_MODELS_DISPLAY = {
    "virtio": "Virtio (Recomendado)",
    "e1000": "Intel e1000",
    "rtl8139": "Realtek RTL8139",
    "i82559er": "Intel i82559ER",
    "pcnet": "AMD PCNet",
    "ne2k_pci": "NE2000 PCI",
}

# MTU
MTU_MIN = 68
MTU_MAX = 65535
MTU_DEFAULT = 1500

# VLAN
VLAN_MIN = 0
VLAN_MAX = 4094
VLAN_DEFAULT = 0

# ==================== CONFIGURACIÓN DE AUDIO ====================

# Drivers de audio
AUDIO_DRIVERS = ["pulseaudio", "alsa", "oss", "coreaudio", "dsound", "sdl", "none"]
AUDIO_DRIVERS_DISPLAY = {
    "pulseaudio": "PulseAudio",
    "alsa": "ALSA",
    "oss": "OSS",
    "coreaudio": "Core Audio (macOS)",
    "dsound": "DirectSound (Windows)",
    "sdl": "SDL",
    "none": "Ninguno"
}

# Modelos de audio
AUDIO_MODELS = ["ac97", "es1370", "sb16", "hdmi", "ich6", "ich9", "hda"]
AUDIO_MODELS_DISPLAY = {
    "ac97": "AC97",
    "es1370": "Ensoniq ES1370",
    "sb16": "Sound Blaster 16",
    "hdmi": "HDMI",
    "ich6": "Intel ICH6",
    "ich9": "Intel ICH9",
    "hda": "Intel HDA"
}

# Volumen
VOLUME_MIN = 0
VOLUME_MAX = 100
VOLUME_DEFAULT = 80

# ==================== CONFIGURACIÓN DE ENTRADA ====================

# Tipos de ratón
MOUSE_TYPES = ["PS/2", "USB", "Tablet USB", "Tablet Wacom"]

# Tipos de teclado
KEYBOARD_TYPES = ["PS/2", "USB"]

# ==================== CONFIGURACIÓN USB ====================

# Versiones USB
USB_VERSIONS = ["1.1", "2.0", "3.0", "3.1"]

# Número de puertos
USB_PORTS_MIN = 1
USB_PORTS_MAX = 16
USB_PORTS_DEFAULT = 4

# ==================== CONFIGURACIÓN PUERTO SERIAL ====================

# Tipos de dispositivo serial
SERIAL_DEVICE_TYPES = ["pty", "file", "socket", "tcp", "udp", "chardev"]

# Puertos
SERIAL_PORT_MIN = 1024
SERIAL_PORT_MAX = 65535
SERIAL_PORT_DEFAULT = 4555

# ==================== CONFIGURACIÓN DEL SISTEMA OPERATIVO ====================

# Tipos de SO
OS_TYPES = ["Linux", "Windows", "macOS", "BSD", "Solaris", "Otro"]

# SO común con configuraciones presets
OS_PRESETS = {
    "Linux (Debian/Ubuntu)": {
        "cpus": 2,
        "ram": 2048,
        "disk": 20,
        "vga": "virtio",
        "network": "virtio",
    },
    "Windows 10": {
        "cpus": 4,
        "ram": 4096,
        "disk": 50,
        "vga": "qxl",
        "network": "e1000",
    },
    "Windows Server 2019": {
        "cpus": 4,
        "ram": 8192,
        "disk": 100,
        "vga": "qxl",
        "network": "e1000",
    },
    "macOS": {
        "cpus": 4,
        "ram": 4096,
        "disk": 80,
        "vga": "vmware",
        "network": "e1000",
    },
}

# ==================== CONFIGURACIÓN DE APLICACIÓN ====================

# Información de la aplicación
APP_NAME = "QEMU Manager"
APP_VERSION = "3.0"
APP_AUTHOR = "QEMU Manager Team"
APP_DESCRIPTION = "Gestor gráfico de máquinas virtuales QEMU"

# Interfaz
WINDOW_MIN_WIDTH = 1200
WINDOW_MIN_HEIGHT = 700
WINDOW_DEFAULT_WIDTH = 1400
WINDOW_DEFAULT_HEIGHT = 800

# Temas
THEME_LIGHT = "light"
THEME_DARK = "dark"
THEME_AUTO = "auto"
THEME_DEFAULT = THEME_AUTO

# Idiomas
LANGUAGE_ES = "es"
LANGUAGE_EN = "en"
LANGUAGE_DEFAULT = LANGUAGE_ES

# ==================== CONFIGURACIÓN DE LOGGING ====================

# Niveles de log
LOG_LEVEL = logging.INFO
LOG_FORMAT = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
LOG_DATE_FORMAT = '%Y-%m-%d %H:%M:%S'

# Rotación de logs
LOG_MAX_SIZE = 10 * 1024 * 1024  # 10 MB
LOG_BACKUP_COUNT = 5

# ==================== CONFIGURACIÓN DE CACHÉ ====================

# Duración del caché (segundos)
CACHE_VM_LIST_TTL = 300  # 5 minutos
CACHE_DISK_LIST_TTL = 600  # 10 minutos
CACHE_SYSTEM_INFO_TTL = 3600  # 1 hora

# ==================== CONFIGURACIÓN DE TIMEOUTS ====================

# Timeouts (segundos)
QEMU_COMMAND_TIMEOUT = 30
QEMU_STOP_TIMEOUT = 5
DISK_OPERATION_TIMEOUT = 300
SYSTEM_CHECK_TIMEOUT = 5

# ==================== CONFIGURACIÓN DE SEGURIDAD ====================

# Validaciones
MIN_VM_NAME_LENGTH = 1
MAX_VM_NAME_LENGTH = 64

# Caracteres permitidos en nombres
VALID_NAME_CHARS = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789-_"

# Rutas restringidas (no permitir crear VMs aquí)
RESTRICTED_PATHS = [
    "/",
    "/boot",
    "/etc",
    "/sys",
    "/proc",
    "/dev",
    "/root",
]

# ==================== CONFIGURACIÓN DE SNAPSHOTS ====================

# Snapshots
SNAPSHOT_FORMAT = "qcow2"
SNAPSHOT_COMPRESSION = True

# ==================== FUNCIÓN DE UTILIDAD ====================

def get_config_value(key, default=None):
    """
    Obtiene valor de configuración dinámicamente
    
    Ejemplo:
        ram = get_config_value('RAM_DEFAULT', 1024)
    """
    import sys
    module = sys.modules[__name__]
    return getattr(module, key, default)


def get_all_config():
    """Retorna diccionario con toda la configuración"""
    import sys
    module = sys.modules[__name__]
    return {
        key: getattr(module, key)
        for key in dir(module)
        if not key.startswith('_') and key.isupper()
    }


def print_config():
    """Imprime toda la configuración (para debugging)"""
    import pprint
    config = get_all_config()
    pprint.pprint(config)


# ==================== VALIDADORES ====================

def is_valid_vm_name(name):
    """Valida nombre de VM"""
    if not name or len(name) > MAX_VM_NAME_LENGTH:
        return False
    return all(c in VALID_NAME_CHARS for c in name)


def is_valid_path(path):
    """Valida ruta"""
    path = Path(path)
    return path.exists() or path.parent.exists()


def is_restricted_path(path):
    """Verifica si es una ruta restringida"""
    path = str(Path(path).absolute())
    return any(path.startswith(restricted) for restricted in RESTRICTED_PATHS)


# ==================== DETECCIÓN DEL SISTEMA ====================

def detect_os_type():
    """Detecta tipo de sistema operativo"""
    import platform
    return platform.system()


def is_windows():
    return detect_os_type() == "Windows"


def is_linux():
    return detect_os_type() == "Linux"


def is_macos():
    return detect_os_type() == "Darwin"


# ==================== INICIALIZACIÓN ====================

if __name__ == "__main__":
    print("=== CONFIGURACIÓN DE QEMU MANAGER ===\n")
    print(f"Versión: {APP_VERSION}")
    print(f"Directorio de configuración: {CONFIG_DIR}")
    print(f"Directorio de logs: {LOGS_DIR}")
    print(f"\nArchivos de configuración:")
    print(f"  - VMs: {VMS_CONFIG_FILE}")
    print(f"  - Discos: {DISKS_CONFIG_FILE}")
    print(f"  - Redes: {NETWORKS_CONFIG_FILE}")
    print(f"\nArchivos de log:")
    print(f"  - Principal: {MAIN_LOG_FILE}")
    print(f"  - Errores: {ERROR_LOG_FILE}")
    print(f"\nPasos para ver toda la configuración:")
    print("  from config import print_config")
    print("  print_config()")
