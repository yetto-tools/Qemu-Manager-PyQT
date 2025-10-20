@echo off
REM setup-windows.bat - Script de instalación para Windows
REM UBICACIÓN: En la raíz del proyecto (qemu-manager/)
REM USAR: Ejecutar como Administrador

setlocal enabledelayedexpansion
chcp 65001 > nul

echo.
echo ============================================================
echo   QEMU Manager - Instalación en Windows
echo ============================================================
echo.

REM ==================== PASO 1: Verificar Python ====================
echo [1/6] Verificando Python...
python --version > nul 2>&1
if errorlevel 1 (
    echo.
    echo ❌ ERROR: Python no está instalado
    echo.
    echo Descarga Python desde: https://www.python.org/downloads/
    echo Asegúrate de marcar "Add Python to PATH" durante la instalación
    echo.
    pause
    exit /b 1
)
for /f "tokens=*" %%i in ('python --version') do set PYTHON_VERSION=%%i
echo 🆗 %PYTHON_VERSION% encontrado
echo.

REM ==================== PASO 2: Verificar si estamos en la carpeta correcta ====================
echo [2/6] Verificando directorio...
if not exist "main.py" (
    echo.
    echo ❌ ERROR: main.py no encontrado
    echo.
    echo Ejecuta este script desde la raíz del proyecto
    echo Ejemplo: D:\VMQemu\qemu-gui-pyqt\qemu-manager\setup-windows.bat
    echo.
    pause
    exit /b 1
)
echo 🆗 Carpeta correcta: %cd%
echo.

REM ==================== PASO 3: Crear entorno virtual ====================
echo [3/6] Creando entorno virtual...
if exist "venv" (
    echo ⚠️  El entorno virtual 'venv' ya existe
    echo ¿Quieres recrearlo? (S/N)
    set /p RECREATE=
    if /i "!RECREATE!"=="S" (
        rmdir /s /q venv
        python -m venv venv
        echo 🆗 Entorno virtual recreado
    ) else (
        echo 🆗 Usando entorno existente
    )
) else (
    python -m venv venv
    echo 🆗 Entorno virtual creado
)
echo.

REM ==================== PASO 4: Activar entorno virtual ====================
echo [4/6] Activando entorno virtual...
call venv\Scripts\activate.bat
echo 🆗 Entorno activado
echo.

REM ==================== PASO 5: Instalar dependencias ====================
echo [5/6] Instalando dependencias Python...
echo.

REM Actualizar pip
echo   - Actualizando pip...
python -m pip install --upgrade pip setuptools wheel > nul 2>&1
echo     🆗 pip actualizado

REM Instalar PyQt5
echo   - Instalando PyQt5...
pip install PyQt5==5.15.9 > nul 2>&1
if errorlevel 1 (
    echo     ❌ Error instalando PyQt5
    pause
    exit /b 1
)
echo     🆗 PyQt5 instalado

REM Instalar psutil
echo   - Instalando psutil...
pip install psutil > nul 2>&1
if errorlevel 1 (
    echo     ❌ Error instalando psutil
    pause
    exit /b 1
)
echo     🆗 psutil instalado

echo.
echo 🆗 Todas las dependencias Python instaladas
echo.

REM ==================== PASO 6: Verificar QEMU ====================
echo [6/6] Verificando QEMU...
echo.

where qemu-system-x86_64 > nul 2>&1
if errorlevel 1 (
    echo ❌ QEMU no está instalado
    echo.
    echo Para instalar QEMU:
    echo.
    echo OPCIÓN 1: Descargar el instalador
    echo   - Ve a: https://www.qemu.org/download/
    echo   - Descarga: qemu-w64-setup-XXXXX.exe (para 64 bits)
    echo   - Ejecuta el instalador
    echo   - Marca "Add QEMU to PATH"
    echo.
    echo OPCIÓN 2: Usar Chocolatey (si lo tienes instalado)
    echo   - Ejecuta: choco install qemu
    echo.
    echo OPCIÓN 3: Usar Windows Subsystem for Linux (WSL)
    echo   - Instala WSL2: https://docs.microsoft.com/en-us/windows/wsl/install
    echo   - Dentro de WSL: sudo apt install qemu-system-x86
    echo.
    pause
) else (
    for /f "tokens=*" %%i in ('qemu-system-x86_64 --version') do set QEMU_VERSION=%%i
    echo 🆗 QEMU encontrado: !QEMU_VERSION!
    echo.
)

where qemu-img > nul 2>&1
if errorlevel 1 (
    echo ⚠️  qemu-img no encontrado (se instala con QEMU)
) else (
    echo 🆗 qemu-img encontrado
    echo.
)

REM ==================== RESUMEN FINAL ====================
echo.
echo ============================================================
echo   🆗 Instalación Completada
echo ============================================================
echo.
echo PRÓXIMOS PASOS:
echo.
echo 1. Abre una nueva Terminal (PowerShell o CMD)
echo 2. Navega a: %cd%
echo 3. Ejecuta: python main.py
echo.
echo O directamente ejecuta desde aquí:
echo.
pause
cls
python main.py