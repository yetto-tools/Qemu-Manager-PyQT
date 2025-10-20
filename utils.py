# utils.py
"""
utils.py - Utilidades centralizadas de la aplicación QEMU Manager

UBICACIÓN: En nivel ROOT (mismo nivel que main.py)
ACCESO: from utils import ...

Este módulo contiene funciones de utilidad compartidas por toda la aplicación
"""

import subprocess
import logging
import json
import os
import sys
from pathlib import Path
from typing import Dict, List, Tuple, Optional, Any
from datetime import datetime
import re
import shutil
import psutil  # Para obtener información del sistema

import config

# ==================== CONFIGURACIÓN DE LOGGING ====================

def setup_logging():
    """
    Configura el sistema de logging de la aplicación
    
    Retorna:
        logger: Logger configurado
    """
    # Crear directorio de logs si no existe
    config.LOGS_DIR.mkdir(parents=True, exist_ok=True)
    
    # Crear logger
    logger = logging.getLogger('qemu_manager')
    logger.setLevel(config.LOG_LEVEL)
    
    # Formato
    formatter = logging.Formatter(
        config.LOG_FORMAT,
        datefmt=config.LOG_DATE_FORMAT
    )
    
    # Handler para archivo
    file_handler = logging.FileHandler(config.MAIN_LOG_FILE)
    file_handler.setLevel(config.LOG_LEVEL)
    file_handler.setFormatter(formatter)
    logger.addHandler(file_handler)
    
    # Handler para error
    error_handler = logging.FileHandler(config.ERROR_LOG_FILE)
    error_handler.setLevel(logging.ERROR)
    error_handler.setFormatter(formatter)
    logger.addHandler(error_handler)
    
    # Handler para consola
    console_handler = logging.StreamHandler()
    console_handler.setLevel(config.LOG_LEVEL)
    console_handler.setFormatter(formatter)
    logger.addHandler(console_handler)
    
    return logger


# Logger global
logger = setup_logging()


# ==================== UTILIDADES DE SISTEMA ====================

def check_qemu_installed() -> bool:
    """
    Verifica si QEMU está instalado en el sistema
    
    Retorna:
        bool: True si QEMU está disponible, False en caso contrario
    """
    try:
        result = subprocess.run(
            [config.QEMU_BINARY, "--version"],
            capture_output=True,
            text=True,
            timeout=config.SYSTEM_CHECK_TIMEOUT
        )
        logger.info(f"QEMU instalado: {result.stdout.strip()}")
        return result.returncode == 0
    except FileNotFoundError:
        logger.error("QEMU no encontrado en el sistema")
        return False
    except subprocess.TimeoutExpired:
        logger.error("Timeout verificando QEMU")
        return False
    except Exception as e:
        logger.error(f"Error verificando QEMU: {e}")
        return False


def check_qemu_img_installed() -> bool:
    """
    Verifica si qemu-img está instalado
    
    Retorna:
        bool: True si qemu-img está disponible
    """
    try:
        result = subprocess.run(
            [config.QEMU_IMG_BINARY, "--version"],
            capture_output=True,
            text=True,
            timeout=config.SYSTEM_CHECK_TIMEOUT
        )
        return result.returncode == 0
    except Exception as e:
        logger.error(f"Error verificando qemu-img: {e}")
        return False


def is_kvm_available() -> bool:
    """
    Verifica si KVM (aceleración de hardware) está disponible
    
    Retorna:
        bool: True si /dev/kvm existe y es accesible
    """
    try:
        kvm_path = Path("/dev/kvm")
        is_available = kvm_path.exists()
        if is_available:
            logger.info("KVM disponible")
        else:
            logger.warning("KVM no disponible - rendimiento será más lento")
        return is_available
    except Exception as e:
        logger.warning(f"No se pudo verificar KVM: {e}")
        return False


def get_system_info() -> Dict[str, Any]:
    """
    Obtiene información del sistema operativo
    
    Retorna:
        dict: Información del sistema
    """
    try:
        import platform
        return {
            'system': platform.system(),
            'release': platform.release(),
            'version': platform.version(),
            'machine': platform.machine(),
            'processor': platform.processor(),
            'python_version': platform.python_version(),
            'cpu_count': os.cpu_count(),
            'total_memory_gb': psutil.virtual_memory().total / (1024**3),
            'available_memory_gb': psutil.virtual_memory().available / (1024**3),
        }
    except Exception as e:
        logger.error(f"Error obteniendo información del sistema: {e}")
        return {}


def get_qemu_version() -> Optional[str]:
    """
    Obtiene versión de QEMU instalada
    
    Retorna:
        str: Versión de QEMU o None
    """
    try:
        result = subprocess.run(
            [config.QEMU_BINARY, "--version"],
            capture_output=True,
            text=True,
            timeout=config.SYSTEM_CHECK_TIMEOUT
        )
        if result.returncode == 0:
            # Parsear versión del output
            version_line = result.stdout.split('\n')[0]
            logger.info(f"Versión QEMU: {version_line}")
            return version_line
    except Exception as e:
        logger.error(f"Error obteniendo versión QEMU: {e}")
    return None


def check_disk_space(path: str) -> Tuple[float, float, float]:
    """
    Obtiene información de espacio en disco
    
    Argumentos:
        path: Ruta a verificar
    
    Retorna:
        tuple: (total_gb, usado_gb, disponible_gb)
    """
    try:
        usage = shutil.disk_usage(path)
        return (
            usage.total / (1024**3),
            usage.used / (1024**3),
            usage.free / (1024**3)
        )
    except Exception as e:
        logger.error(f"Error obteniendo espacio en disco: {e}")
        return (0, 0, 0)


# ==================== UTILIDADES DE VALIDACIÓN ====================

def validate_vm_name(name: str) -> Tuple[bool, str]:
    """
    Valida un nombre de máquina virtual
    
    Argumentos:
        name: Nombre a validar
    
    Retorna:
        tuple: (es_válido, mensaje_error)
    """
    if not name:
        return False, "El nombre no puede estar vacío"
    
    if len(name) > config.MAX_VM_NAME_LENGTH:
        return False, f"El nombre no puede exceder {config.MAX_VM_NAME_LENGTH} caracteres"
    
    if not config.is_valid_vm_name(name):
        return False, f"El nombre contiene caracteres inválidos. Permitidos: {config.VALID_NAME_CHARS}"
    
    return True, ""


def validate_disk_path(path: str) -> Tuple[bool, str]:
    """
    Valida una ruta de disco
    
    Argumentos:
        path: Ruta a validar
    
    Retorna:
        tuple: (es_válido, mensaje_error)
    """
    if not path:
        return False, "La ruta no puede estar vacía"
    
    path_obj = Path(path)
    
    if config.is_restricted_path(path):
        return False, f"No se puede crear disco en ruta restringida: {path}"
    
    parent = path_obj.parent
    if not parent.exists():
        return False, f"El directorio padre no existe: {parent}"
    
    return True, ""


def validate_disk_size(size_gb: float) -> Tuple[bool, str]:
    """
    Valida tamaño de disco
    
    Argumentos:
        size_gb: Tamaño en GB
    
    Retorna:
        tuple: (es_válido, mensaje_error)
    """
    if size_gb <= 0:
        return False, "El tamaño debe ser mayor a 0"
    
    if size_gb > 2000:
        return False, "El tamaño no puede exceder 2000 GB"
    
    return True, ""


def validate_ram(ram_mb: int) -> Tuple[bool, str]:
    """
    Valida cantidad de RAM
    
    Argumentos:
        ram_mb: RAM en MB
    
    Retorna:
        tuple: (es_válido, mensaje_error)
    """
    if ram_mb < config.RAM_MIN:
        return False, f"RAM mínima: {config.RAM_MIN} MB"
    
    if ram_mb > config.RAM_MAX:
        return False, f"RAM máxima: {config.RAM_MAX} MB"
    
    return True, ""


def validate_cpu_cores(cores: int) -> Tuple[bool, str]:
    """
    Valida cantidad de núcleos CPU
    
    Argumentos:
        cores: Número de núcleos
    
    Retorna:
        tuple: (es_válido, mensaje_error)
    """
    if cores < config.CPU_MIN:
        return False, f"CPU mínima: {config.CPU_MIN} núcleo(s)"
    
    if cores > config.CPU_MAX:
        return False, f"CPU máxima: {config.CPU_MAX} núcleos"
    
    return True, ""


# ==================== UTILIDADES DE ARCHIVO ====================

def save_json(data: Dict, filepath: Path) -> bool:
    """
    Guarda datos en archivo JSON
    
    Argumentos:
        data: Diccionario a guardar
        filepath: Ruta del archivo
    
    Retorna:
        bool: True si se guardó exitosamente
    """
    try:
        filepath.parent.mkdir(parents=True, exist_ok=True)
        with open(filepath, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Archivo guardado: {filepath}")
        return True
    except Exception as e:
        logger.error(f"Error guardando JSON: {e}")
        return False


def load_json(filepath: Path) -> Dict:
    """
    Carga datos desde archivo JSON
    
    Argumentos:
        filepath: Ruta del archivo
    
    Retorna:
        dict: Datos cargados o {} si falla
    """
    try:
        if filepath.exists():
            with open(filepath, 'r') as f:
                data = json.load(f)
            logger.info(f"Archivo cargado: {filepath}")
            return data
    except json.JSONDecodeError as e:
        logger.error(f"Error decodificando JSON: {e}")
    except Exception as e:
        logger.error(f"Error cargando JSON: {e}")
    
    return {}


def backup_file(filepath: Path) -> Optional[Path]:
    """
    Crea copia de seguridad de un archivo
    
    Argumentos:
        filepath: Ruta del archivo a respaldar
    
    Retorna:
        Path: Ruta del archivo de respaldo o None si falla
    """
    try:
        if not filepath.exists():
            return None
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        backup_path = config.BACKUP_DIR / f"{filepath.stem}_{timestamp}{filepath.suffix}"
        
        backup_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(filepath, backup_path)
        logger.info(f"Backup creado: {backup_path}")
        return backup_path
    except Exception as e:
        logger.error(f"Error creando backup: {e}")
        return None


def clean_old_backups(days: int = 30) -> int:
    """
    Elimina respaldos más antiguos que X días
    
    Argumentos:
        days: Número de días
    
    Retorna:
        int: Cantidad de archivos eliminados
    """
    try:
        import time
        current_time = time.time()
        deleted_count = 0
        
        for backup_file in config.BACKUP_DIR.glob("*"):
            if backup_file.is_file():
                file_age_days = (current_time - backup_file.stat().st_mtime) / 86400
                if file_age_days > days:
                    backup_file.unlink()
                    deleted_count += 1
                    logger.info(f"Backup antiguo eliminado: {backup_file}")
        
        return deleted_count
    except Exception as e:
        logger.error(f"Error limpiando backups: {e}")
        return 0


# ==================== UTILIDADES DE EJECUCIÓN DE COMANDOS ====================

def run_command(command: str, timeout: int = config.QEMU_COMMAND_TIMEOUT) -> Tuple[int, str, str]:
    """
    Ejecuta comando en shell
    
    Argumentos:
        command: Comando a ejecutar
        timeout: Timeout en segundos
    
    Retorna:
        tuple: (código_retorno, stdout, stderr)
    """
    try:
        result = subprocess.run(
            command,
            shell=True,
            capture_output=True,
            text=True,
            timeout=timeout
        )
        logger.debug(f"Comando ejecutado: {command}")
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        logger.error(f"Timeout ejecutando comando: {command}")
        return -1, "", "Timeout"
    except Exception as e:
        logger.error(f"Error ejecutando comando: {e}")
        return -1, "", str(e)


def run_command_async(command: str) -> Optional[subprocess.Popen]:
    """
    Ejecuta comando de forma asíncrona
    
    Argumentos:
        command: Comando a ejecutar
    
    Retorna:
        Popen: Objeto del proceso o None si falla
    """
    try:
        process = subprocess.Popen(
            command,
            shell=True,
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            text=True
        )
        logger.info(f"Proceso iniciado: {command} (PID: {process.pid})")
        return process
    except Exception as e:
        logger.error(f"Error iniciando proceso: {e}")
        return None


def get_process_info(pid: int) -> Optional[Dict]:
    """
    Obtiene información de un proceso
    
    Argumentos:
        pid: ID del proceso
    
    Retorna:
        dict: Información del proceso o None
    """
    try:
        process = psutil.Process(pid)
        return {
            'pid': process.pid,
            'name': process.name(),
            'status': process.status(),
            'cpu_percent': process.cpu_percent(interval=1),
            'memory_info': process.memory_info().rss / (1024**2),  # MB
            'create_time': datetime.fromtimestamp(process.create_time()),
        }
    except psutil.NoSuchProcess:
        logger.warning(f"Proceso no encontrado: {pid}")
        return None
    except Exception as e:
        logger.error(f"Error obteniendo info del proceso: {e}")
        return None


# ==================== UTILIDADES DE DISCO ====================

def get_disk_info(disk_path: str) -> Optional[Dict]:
    """
    Obtiene información detallada de un disco QEMU
    
    Argumentos:
        disk_path: Ruta del archivo de disco
    
    Retorna:
        dict: Información del disco o None
    """
    try:
        code, stdout, stderr = run_command(f"{config.QEMU_IMG_BINARY} info '{disk_path}'")
        
        if code == 0:
            info = {}
            for line in stdout.split('\n'):
                if ':' in line:
                    key, value = line.split(':', 1)
                    info[key.strip()] = value.strip()
            
            logger.info(f"Info de disco obtenida: {disk_path}")
            return info
    except Exception as e:
        logger.error(f"Error obteniendo info del disco: {e}")
    
    return None


def get_disk_size(disk_path: str) -> Optional[float]:
    """
    Obtiene tamaño de disco en GB
    
    Argumentos:
        disk_path: Ruta del archivo de disco
    
    Retorna:
        float: Tamaño en GB o None
    """
    try:
        if Path(disk_path).exists():
            size_bytes = Path(disk_path).stat().st_size
            size_gb = size_bytes / (1024**3)
            return size_gb
    except Exception as e:
        logger.error(f"Error obteniendo tamaño del disco: {e}")
    
    return None


# ==================== UTILIDADES DE BÚSQUEDA ====================

def find_disk_images(search_path: str = None, extensions: List[str] = None) -> List[Path]:
    """
    Busca archivos de disco en el sistema
    
    Argumentos:
        search_path: Ruta inicial (por defecto: home)
        extensions: Extensiones a buscar (por defecto: qcow2, img, vdi, vmdk)
    
    Retorna:
        list: Lista de rutas encontradas
    """
    if search_path is None:
        search_paths = config.VM_SEARCH_PATHS
    else:
        search_paths = [search_path]
    
    if extensions is None:
        extensions = ["*.qcow2", "*.img", "*.vdi", "*.vmdk"]
    
    found_images = []
    
    for search_path in search_paths:
        try:
            path_obj = Path(search_path)
            if path_obj.exists():
                for ext in extensions:
                    for image in path_obj.rglob(ext):
                        if image.is_file():
                            found_images.append(image)
                            logger.debug(f"Imagen encontrada: {image}")
        except Exception as e:
            logger.warning(f"Error buscando en {search_path}: {e}")
    
    logger.info(f"Se encontraron {len(found_images)} imagen(es) de disco")
    return found_images


def find_iso_images(search_path: str = None) -> List[Path]:
    """
    Busca archivos ISO en el sistema
    
    Argumentos:
        search_path: Ruta inicial
    
    Retorna:
        list: Lista de ISOs encontradas
    """
    if search_path is None:
        search_path = str(Path.home())
    
    try:
        found_isos = list(Path(search_path).rglob("*.iso"))
        logger.info(f"Se encontraron {len(found_isos)} ISO(s)")
        return found_isos
    except Exception as e:
        logger.error(f"Error buscando ISOs: {e}")
        return []


# ==================== UTILIDADES DE CONVERSIÓN ====================

def bytes_to_human_readable(size_bytes: float) -> str:
    """
    Convierte bytes a formato legible
    
    Argumentos:
        size_bytes: Tamaño en bytes
    
    Retorna:
        str: Tamaño formateado
    """
    for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
        if size_bytes < 1024:
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024
    return f"{size_bytes:.2f} PB"


def seconds_to_human_readable(seconds: int) -> str:
    """
    Convierte segundos a formato legible
    
    Argumentos:
        seconds: Tiempo en segundos
    
    Retorna:
        str: Tiempo formateado
    """
    hours = seconds // 3600
    minutes = (seconds % 3600) // 60
    secs = seconds % 60
    
    if hours > 0:
        return f"{hours}h {minutes}m {secs}s"
    elif minutes > 0:
        return f"{minutes}m {secs}s"
    else:
        return f"{secs}s"


# ==================== UTILIDADES DE FORMATO ====================

def sanitize_string(text: str, max_length: int = 100) -> str:
    """
    Sanitiza texto removiendo caracteres especiales
    
    Argumentos:
        text: Texto a sanitizar
        max_length: Longitud máxima
    
    Retorna:
        str: Texto sanitizado
    """
    # Remover caracteres especiales
    text = re.sub(r'[<>:"/\\|?*]', '', text)
    # Limitar longitud
    text = text[:max_length]
    return text


def format_datetime(dt: datetime = None, format_str: str = "%Y-%m-%d %H:%M:%S") -> str:
    """
    Formatea datetime
    
    Argumentos:
        dt: Datetime (por defecto: ahora)
        format_str: Formato de salida
    
    Retorna:
        str: Fecha formateada
    """
    if dt is None:
        dt = datetime.now()
    return dt.strftime(format_str)


# ==================== UTILIDADES DE RED ====================

def is_port_available(port: int) -> bool:
    """
    Verifica si un puerto TCP está disponible
    
    Argumentos:
        port: Número de puerto
    
    Retorna:
        bool: True si está disponible
    """
    import socket
    try:
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('127.0.0.1', port))
        sock.close()
        return result != 0
    except Exception as e:
        logger.error(f"Error verificando puerto: {e}")
        return False


def find_available_port(start_port: int = 5000, end_port: int = 6000) -> Optional[int]:
    """
    Encuentra un puerto TCP disponible
    
    Argumentos:
        start_port: Puerto inicial
        end_port: Puerto final
    
    Retorna:
        int: Puerto disponible o None
    """
    for port in range(start_port, end_port):
        if is_port_available(port):
            logger.info(f"Puerto disponible encontrado: {port}")
            return port
    
    logger.warning("No se encontró puerto disponible")
    return None


# ==================== UTILIDADES DE CACHÉ ====================

class SimpleCache:
    """Caché simple en memoria con TTL"""
    
    def __init__(self):
        self.cache = {}
        self.timestamps = {}
    
    def set(self, key: str, value: Any, ttl: int = 300):
        """Almacena valor en caché"""
        self.cache[key] = value
        self.timestamps[key] = datetime.now()
    
    def get(self, key: str, ttl: int = 300) -> Optional[Any]:
        """Obtiene valor del caché si no ha expirado"""
        if key not in self.cache:
            return None
        
        age = (datetime.now() - self.timestamps[key]).total_seconds()
        if age > ttl:
            del self.cache[key]
            del self.timestamps[key]
            return None
        
        return self.cache[key]
    
    def clear(self):
        """Limpia el caché"""
        self.cache.clear()
        self.timestamps.clear()


# Instancia global de caché
cache = SimpleCache()


# ==================== FUNCIÓN PRINCIPAL DE DIAGNÓSTICO ====================

def run_diagnostics() -> Dict[str, Any]:
    """
    Ejecuta diagnóstico completo del sistema
    
    Retorna:
        dict: Resultados del diagnóstico
    """
    logger.info("=== Iniciando diagnóstico del sistema ===")
    
    diagnostics = {
        'timestamp': format_datetime(),
        'system_info': get_system_info(),
        'qemu_installed': check_qemu_installed(),
        'qemu_img_installed': check_qemu_img_installed(),
        'qemu_version': get_qemu_version(),
        'kvm_available': is_kvm_available(),
        'config_dir': str(config.CONFIG_DIR),
        'config_dir_exists': config.CONFIG_DIR.exists(),
        'disk_space': {
            'home': {
                'total_gb': check_disk_space(str(Path.home()))[0],
                'available_gb': check_disk_space(str(Path.home()))[2]
            }
        }
    }
    
    logger.info("=== Diagnóstico completado ===")
    return diagnostics


    print("✓ Sistema diagnosticado correctamente")


# ==================== DECORADORES ÚTILES ====================

def log_execution(func):
    """
    Decorador que registra ejecución de funciones
    
    Uso:
        @log_execution
        def mi_funcion():
            pass
    """
    def wrapper(*args, **kwargs):
        func_name = func.__name__
        logger.info(f"Iniciando: {func_name}")
        try:
            result = func(*args, **kwargs)
            logger.info(f"Completado: {func_name}")
            return result
        except Exception as e:
            logger.error(f"Error en {func_name}: {e}")
            raise
    return wrapper


def retry(max_attempts: int = 3, delay: int = 1):
    """
    Decorador para reintentar función en caso de fallo
    
    Uso:
        @retry(max_attempts=3, delay=2)
        def operacion_critica():
            pass
    """
    def decorator(func):
        def wrapper(*args, **kwargs):
            import time
            for attempt in range(max_attempts):
                try:
                    return func(*args, **kwargs)
                except Exception as e:
                    if attempt == max_attempts - 1:
                        logger.error(f"Fallo tras {max_attempts} intentos: {e}")
                        raise
                    logger.warning(f"Intento {attempt + 1} falló, reintentando en {delay}s...")
                    time.sleep(delay)
        return wrapper
    return decorator


def timing(func):
    """
    Decorador que mide tiempo de ejecución
    
    Uso:
        @timing
        def operacion_lenta():
            pass
    """
    def wrapper(*args, **kwargs):
        import time
        start = time.time()
        result = func(*args, **kwargs)
        elapsed = time.time() - start
        logger.info(f"{func.__name__} tardó {elapsed:.2f}s")
        return result
    return wrapper


# ==================== UTILIDADES DE ESTADÍSTICAS ====================

class SystemMonitor:
    """Monitor de recursos del sistema"""
    
    @staticmethod
    def get_cpu_usage() -> float:
        """Obtiene uso de CPU en porcentaje"""
        try:
            return psutil.cpu_percent(interval=1)
        except Exception as e:
            logger.error(f"Error obteniendo CPU: {e}")
            return 0.0
    
    @staticmethod
    def get_memory_usage() -> Dict[str, float]:
        """Obtiene uso de memoria"""
        try:
            mem = psutil.virtual_memory()
            return {
                'total_gb': mem.total / (1024**3),
                'used_gb': mem.used / (1024**3),
                'available_gb': mem.available / (1024**3),
                'percent': mem.percent
            }
        except Exception as e:
            logger.error(f"Error obteniendo memoria: {e}")
            return {}
    
    @staticmethod
    def get_disk_usage_all() -> Dict[str, Dict]:
        """Obtiene uso de disco de todas las particiones"""
        try:
            result = {}
            for partition in psutil.disk_partitions():
                try:
                    usage = psutil.disk_usage(partition.mountpoint)
                    result[partition.mountpoint] = {
                        'total_gb': usage.total / (1024**3),
                        'used_gb': usage.used / (1024**3),
                        'free_gb': usage.free / (1024**3),
                        'percent': usage.percent
                    }
                except:
                    pass
            return result
        except Exception as e:
            logger.error(f"Error obteniendo discos: {e}")
            return {}
    
    @staticmethod
    def get_network_stats() -> Dict:
        """Obtiene estadísticas de red"""
        try:
            net_io = psutil.net_io_counters()
            return {
                'bytes_sent_mb': net_io.bytes_sent / (1024**2),
                'bytes_recv_mb': net_io.bytes_recv / (1024**2),
                'packets_sent': net_io.packets_sent,
                'packets_recv': net_io.packets_recv,
                'errors_in': net_io.errin,
                'errors_out': net_io.errout,
            }
        except Exception as e:
            logger.error(f"Error obteniendo estadísticas de red: {e}")
            return {}
    
    @staticmethod
    def get_overall_stats() -> Dict[str, Any]:
        """Obtiene estadísticas generales del sistema"""
        return {
            'timestamp': format_datetime(),
            'cpu_percent': SystemMonitor.get_cpu_usage(),
            'memory': SystemMonitor.get_memory_usage(),
            'disks': SystemMonitor.get_disk_usage_all(),
            'network': SystemMonitor.get_network_stats(),
        }


# ==================== UTILIDADES DE PROCESAMIENTO ====================

class BatchProcessor:
    """Procesa lotes de elementos"""
    
    def __init__(self, batch_size: int = 100):
        self.batch_size = batch_size
    
    def process_batch(self, items: List[Any], callback) -> List[Any]:
        """
        Procesa elementos en lotes
        
        Argumentos:
            items: Lista de elementos
            callback: Función de procesamiento
        
        Retorna:
            list: Resultados procesados
        """
        results = []
        
        for i in range(0, len(items), self.batch_size):
            batch = items[i:i + self.batch_size]
            logger.info(f"Procesando lote {i//self.batch_size + 1}")
            
            for item in batch:
                try:
                    result = callback(item)
                    results.append(result)
                except Exception as e:
                    logger.error(f"Error procesando {item}: {e}")
        
        return results


# ==================== UTILIDADES DE COMPATIBILIDAD ====================

def ensure_path_exists(path: str) -> Path:
    """
    Asegura que una ruta existe, crea si no existe
    
    Argumentos:
        path: Ruta a verificar/crear
    
    Retorna:
        Path: Ruta verificada
    """
    path_obj = Path(path)
    path_obj.mkdir(parents=True, exist_ok=True)
    return path_obj


def copy_file_safe(source: str, destination: str) -> bool:
    """
    Copia archivo de forma segura
    
    Argumentos:
        source: Archivo origen
        destination: Archivo destino
    
    Retorna:
        bool: True si se copió exitosamente
    """
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            logger.error(f"Archivo origen no existe: {source}")
            return False
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        shutil.copy2(source_path, dest_path)
        logger.info(f"Archivo copiado: {source} -> {destination}")
        return True
    except Exception as e:
        logger.error(f"Error copiando archivo: {e}")
        return False


def move_file_safe(source: str, destination: str) -> bool:
    """
    Mueve archivo de forma segura
    
    Argumentos:
        source: Archivo origen
        destination: Archivo destino
    
    Retorna:
        bool: True si se movió exitosamente
    """
    try:
        source_path = Path(source)
        dest_path = Path(destination)
        
        if not source_path.exists():
            logger.error(f"Archivo no existe: {source}")
            return False
        
        dest_path.parent.mkdir(parents=True, exist_ok=True)
        source_path.rename(dest_path)
        logger.info(f"Archivo movido: {source} -> {destination}")
        return True
    except Exception as e:
        logger.error(f"Error moviendo archivo: {e}")
        return False


def delete_file_safe(filepath: str) -> bool:
    """
    Elimina archivo de forma segura
    
    Argumentos:
        filepath: Ruta del archivo
    
    Retorna:
        bool: True si se eliminó exitosamente
    """
    try:
        path = Path(filepath)
        if path.exists():
            path.unlink()
            logger.info(f"Archivo eliminado: {filepath}")
            return True
        else:
            logger.warning(f"Archivo no existe: {filepath}")
            return False
    except Exception as e:
        logger.error(f"Error eliminando archivo: {e}")
        return False


# ==================== UTILIDADES DE CONFIGURACIÓN DINÁMICA ====================

def load_env_file(env_path: str = ".env") -> Dict[str, str]:
    """
    Carga variables de archivo .env
    
    Argumentos:
        env_path: Ruta del archivo .env
    
    Retorna:
        dict: Variables cargadas
    """
    env_vars = {}
    env_file = Path(env_path)
    
    if not env_file.exists():
        logger.warning(f"Archivo .env no encontrado: {env_path}")
        return env_vars
    
    try:
        with open(env_file, 'r') as f:
            for line in f:
                line = line.strip()
                if line and not line.startswith('#') and '=' in line:
                    key, value = line.split('=', 1)
                    env_vars[key.strip()] = value.strip().strip('"\'')
        
        logger.info(f"Variables cargadas desde {env_path}: {len(env_vars)}")
    except Exception as e:
        logger.error(f"Error cargando .env: {e}")
    
    return env_vars


# ==================== UTILIDADES DE COMPARACIÓN ====================

def compare_configs(config1: Dict, config2: Dict) -> Dict[str, Any]:
    """
    Compara dos configuraciones
    
    Argumentos:
        config1: Primera configuración
        config2: Segunda configuración
    
    Retorna:
        dict: Diferencias encontradas
    """
    differences = {
        'added': {},
        'removed': {},
        'modified': {}
    }
    
    # Elementos añadidos
    for key, value in config2.items():
        if key not in config1:
            differences['added'][key] = value
    
    # Elementos removidos
    for key, value in config1.items():
        if key not in config2:
            differences['removed'][key] = value
    
    # Elementos modificados
    for key in config1:
        if key in config2 and config1[key] != config2[key]:
            differences['modified'][key] = {
                'old': config1[key],
                'new': config2[key]
            }
    
    logger.info(f"Comparación completada: {len(differences['modified'])} diferencias")
    return differences


# ==================== UTILIDADES DE GENERACIÓN ====================

def generate_unique_name(prefix: str = "vm", existing: List[str] = None) -> str:
    """
    Genera nombre único para VM
    
    Argumentos:
        prefix: Prefijo del nombre
        existing: Lista de nombres existentes
    
    Retorna:
        str: Nombre único generado
    """
    if existing is None:
        existing = []
    
    counter = 1
    while True:
        name = f"{prefix}_{counter}"
        if name not in existing:
            logger.info(f"Nombre único generado: {name}")
            return name
        counter += 1


def generate_mac_address() -> str:
    """
    Genera dirección MAC aleatoria válida
    
    Retorna:
        str: Dirección MAC en formato 00:11:22:33:44:55
    """
    import random
    mac = [0x00, 0x16, 0x3e, random.randint(0x00, 0x7f), random.randint(0x00, 0xff), random.randint(0x00, 0xff)]
    mac_str = ':'.join(map(lambda x: "%02x" % x, mac))
    logger.debug(f"MAC address generada: {mac_str}")
    return mac_str


def generate_uuid() -> str:
    """
    Genera UUID único
    
    Retorna:
        str: UUID generado
    """
    import uuid
    new_uuid = str(uuid.uuid4())
    logger.debug(f"UUID generado: {new_uuid}")
    return new_uuid


# ==================== UTILIDADES DE NOTIFICACIÓN ====================

class NotificationCenter:
    """Centro de notificaciones"""
    
    def __init__(self):
        self.observers = {}
    
    def subscribe(self, event: str, callback):
        """Suscribirse a un evento"""
        if event not in self.observers:
            self.observers[event] = []
        self.observers[event].append(callback)
        logger.debug(f"Observador suscrito a: {event}")
    
    def unsubscribe(self, event: str, callback):
        """Desuscribirse de un evento"""
        if event in self.observers and callback in self.observers[event]:
            self.observers[event].remove(callback)
            logger.debug(f"Observador desuscrito de: {event}")
    
    def notify(self, event: str, data: Any = None):
        """Notifica a todos los observadores"""
        if event in self.observers:
            for callback in self.observers[event]:
                try:
                    callback(data)
                except Exception as e:
                    logger.error(f"Error notificando evento {event}: {e}")


# Instancia global
notification_center = NotificationCenter()


# ==================== SCRIPT DE PRUEBA ====================

if __name__ == "__main__":
    print("=== UTILIDADES QEMU MANAGER ===\n")
    print("Ejecutando diagnóstico del sistema...\n")
    
    # Diagnóstico del sistema
    diag = run_diagnostics()
    
    import pprint
    print("\n--- Diagnóstico del Sistema ---")
    pprint.pprint(diag)
    
    # Estadísticas del monitor
    print("\n--- Estadísticas del Sistema ---")
    stats = SystemMonitor.get_overall_stats()
    pprint.pprint(stats)
    
    # Generación de nombres
    print("\n--- Generación de Nombres ---")
    print(f"Nombre único: {generate_unique_name('vm_test')}")
    print(f"MAC Address: {generate_mac_address()}")
    print(f"UUID: {generate_uuid()}")
    
    # Validaciones
    print("\n--- Validaciones ---")
    is_valid, msg = validate_vm_name("mi_vm_123")
    print(f"VM 'mi_vm_123': {is_valid} - {msg}")
    
    is_valid, msg = validate_vm_name("vm inválido!")
    print(f"VM 'vm inválido!': {is_valid} - {msg}")
    
    is_valid, msg = validate_ram(2048)
    print(f"RAM 2048MB: {is_valid}")
    
    # Conversiones
    print("\n--- Conversiones ---")
    print(f"5368709120 bytes = {bytes_to_human_readable(5368709120)}")
    print(f"3661 segundos = {seconds_to_human_readable(3661)}")
    
    # Búsqueda
    print("\n--- Búsqueda de Imágenes ---")
    disks = find_disk_images()
    print(f"Discos encontrados: {len(disks)}")
    for disk in disks[:3]:
        print(f"  - {disk}")
    
    print("\n✓ Utilidades cargadas correctamente")