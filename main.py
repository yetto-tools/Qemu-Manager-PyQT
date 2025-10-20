# main.py
"""
main.py - Punto de entrada de la aplicación QEMU Manager

UBICACIÓN: En la raíz del proyecto (qemu-manager/main.py)
PROPÓSITO: Inicializar la aplicación con inyección de dependencias
"""
# -*- coding: utf-8 -*-

"""
Punto de entrada principal - QEMU Manager
Inicializa todas las dependencias e inyecta en la UI
"""

import sys
import logging
from pathlib import Path

from PyQt5.QtWidgets import QApplication

# ==================== CONFIGURAR LOGGING ====================

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger('qemu_manager')

# ==================== IMPORTAR CAPAS ====================

# Capa de Dominio
from qemu_domain.models import VirtualMachine, VirtualDisk
from qemu_domain.use_cases import VMUseCase, DiskUseCase
from qemu_domain.repositories import VMRepository, DiskRepository

# Capa de Adaptadores
from qemu_adapters.repositories import JSONVMRepository, JSONDiskRepository
from qemu_adapters.storage_adapter import StorageAdapterImpl
from qemu_adapters.qemu_executor import QEMUExecutorImpl
from qemu_adapters.config_persistence import JSONConfigPersistence

# Capa de Presentación
from qemu_ui.main_window import QEMUManagerUI


def setup_dependencies():
    """Configura todas las dependencias e inyecciones"""

    logger.info("Configurando dependencias...")

    # ==================== PERSISTENCIA ====================

    config_persistence = JSONConfigPersistence()

    # ==================== ADAPTADORES ====================

    storage_adapter = StorageAdapterImpl()
    qemu_executor = QEMUExecutorImpl()

    # ==================== REPOSITORIOS ====================

    vm_repository = JSONVMRepository(config_persistence)
    disk_repository = JSONDiskRepository(config_persistence)
    
    # ==================== CASOS DE USO ====================
    
    vm_use_case = VMUseCase(vm_repository)
    disk_use_case = DiskUseCase(disk_repository)
    
    # ==================== SERVICIOS DE APLICACIÓN ====================
    
    # Placeholder para servicios de aplicación si los necesitas
    app_service = None
    
    # ==================== INYECCIÓN DE DEPENDENCIAS ====================
    
    dependencies = {
        'vm_use_case': vm_use_case,
        'disk_use_case': disk_use_case,
        'app_service': app_service,
        'qemu_executor': qemu_executor,
        'storage': storage_adapter,
    }
    
    logger.info("Dependencias configuradas correctamente")
    
    return dependencies


def main():
    """Punto de entrada principal"""
    
    logger.info("Iniciando QEMU Manager...")
    
    # Crear aplicación Qt
    app = QApplication(sys.argv)
    
    try:
        # Configurar dependencias
        dependencies = setup_dependencies()
        
        # Crear ventana principal con inyección de dependencias
        logger.info("Creando interfaz de usuario...")
        main_window = QEMUManagerUI(dependencies)
        main_window.show()
        
        logger.info("Entrando en loop de eventos...")
        
        # Ejecutar aplicación
        exit_code = app.exec_()
        
        logger.info(f"Aplicación terminada con código: {exit_code}")
        sys.exit(exit_code)
        
    except Exception as e:
        logger.error(f"Error fatal: {e}", exc_info=True)
        sys.exit(1)


if __name__ == "__main__":
    main()


# ==================== NOTAS DE DESARROLLO ====================

"""
NOTAS IMPORTANTES:

1. ESTRUCTURA DE CARPETAS REQUERIDA:
   qemu-manager/
   ├── main.py                    ← Este archivo
   ├── config.py
   ├── utils.py
   ├── qemu_domain/
   ├── qemu_adapters/
   ├── qemu_application/
   └── qemu_ui/

2. FLUJO DE INYECCIÓN DE DEPENDENCIAS:
   
   Configuración
        ↓
   Verificación del Sistema
        ↓
   Persistencia (JSON)
        ↓
   Repositorios (VM, Disco)
        ↓
   Casos de Uso (VM, Disco)
        ↓
   Adaptadores (QEMU, Storage)
        ↓
   Servicios de Aplicación
        ↓
   Interfaz de Usuario (PyQt5)

3. PARA EJECUTAR:
   
   Desde la terminal en el directorio raíz:
   ```
   python main.py
   ```

4. PARA DEBUGGEAR:
   
   Habilitar nivel DEBUG en config.py:
   ```python
   LOG_LEVEL = logging.DEBUG
   ```
   
   Ver logs en:
   ```
   ~/.qemu_manager/logs/qemu_manager.log
   ~/.qemu_manager/logs/debug.log
   ```

5. REQUISITOS PREVIOS:
   
   pip install PyQt5 psutil
   qemu-system-x86_64 --version
   qemu-img --version

6. TROUBLESHOOTING:
   
   Si hay error de "módulo no encontrado":
   - Verificar que los archivos existan
   - Verificar permisos de lectura
   - Verificar ruta del proyecto
   - Ejecutar desde el directorio raíz del proyecto
"""

"""
## Estructura de Carpetas

```
qemu-manager/
├── qemu_domain/                 # Capa de Dominio
│   ├── __init__.py
│   ├── models.py                # Entidades
│   ├── repositories.py          # Interfaces de repositorios
│   └── use_cases.py             # Casos de uso
├── qemu_adapters/               # Capa de Adaptadores
│   ├── __init__.py
│   ├── ports.py                 # Interfaces (puertos)
│   ├── qemu_executor.py         # Ejecución QEMU
│   ├── storage_adapter.py       # Almacenamiento
│   ├── config_persistence.py    # Persistencia
│   └── repositories.py          # Implementación repositorios
├── qemu_application/            # Capa de Aplicación
│   ├── __init__.py
│   ├── service.py               # Servicios
│   └── presenters.py            # Interfaces presentadores
├── qemu_ui/                     # Capa de Presentación
│   ├── __init__.py
│   ├── main_window.py           # Ventana principal
│   └── dialogs/                 # Diálogos
│       ├── disk_manager_dialog.py
│       ├── network_dialog.py
│       ├── video_dialog.py
│       ├── peripherals_dialog.py
│       ├── search_dialog.py
│       └── about_dialog.py
├── tests/                       # Tests unitarios
│   ├── test_vm_use_case.py
│   ├── test_disk_use_case.py
│   └── test_qemu_executor.py
├── main.py                      # Punto de entrada
├── config.py                    # Configuración
├── utils.py                     # Utilidades
├── requirements.txt
└── README.md
```

## Requisitos del Sistema

- Python 3.8+
- QEMU instalado
- PyQt5
- Sistema Linux, macOS o WSL

## Desarrolladores

Para contribuir, crear tests para nuevas funcionalidades:

```bash
python -m pytest tests/
```

## Licencia

GPL v3

## Roadmap

- [ ] Interfaz para VNC integrada
- [ ] Snapshots de máquinas virtuales
- [ ] Monitor de recursos en tiempo real
- [ ] API REST para control remoto
- [ ] Soporte para LibVirt
- [ ] Clonación de VMs
- [ ] Balanceo de recursos

## Contacto

Para reportar bugs o sugerencias, abrir un issue en el repositorio.
"""