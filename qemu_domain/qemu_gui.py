import sys
import os
import subprocess
import json
from pathlib import Path
from PyQt5.QtWidgets import (
    QApplication, QMainWindow, QWidget, QVBoxLayout, QHBoxLayout,
    QPushButton, QLabel, QLineEdit, QSpinBox, QComboBox, QListWidget,
    QListWidgetItem, QTabWidget, QGroupBox, QFileDialog, QMessageBox,
    QCheckBox, QFormLayout, QTableWidget, QTableWidgetItem, QTextEdit,
    QMenu, QDialog, QScrollArea, QProgressBar
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal, QTimer
from PyQt5.QtGui import QFont, QIcon, QColor


class QemuWorker(QThread):
    finished = pyqtSignal()
    error = pyqtSignal(str)
    output = pyqtSignal(str)

    def __init__(self, command):
        super().__init__()
        self.command = command
        self.process = None

    def run(self):
        try:
            env = os.environ.copy()
            self.process = subprocess.Popen(
                self.command,
                shell=True,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE,
                text=True,
                env=env
            )
            stdout, stderr = self.process.communicate()
            if stderr:
                self.error.emit(stderr)
            if stdout:
                self.output.emit(stdout)
            self.finished.emit()
        except Exception as e:
            self.error.emit(str(e))


class AboutDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Acerca de QEMU Manager")
        self.setGeometry(200, 200, 500, 350)
        
        layout = QVBoxLayout()
        
        title = QLabel("QEMU Manager")
        title_font = QFont()
        title_font.setPointSize(16)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        version = QLabel("Versión 2.0")
        version_font = QFont()
        version_font.setPointSize(10)
        version.setFont(version_font)
        layout.addWidget(version)
        
        layout.addSpacing(20)
        
        description = QLabel(
            "Gestor gráfico completo para máquinas virtuales QEMU.\n\n"
            "Características:\n"
            "• Crear y gestionar máquinas virtuales\n"
            "• Detección automática de VMs existentes\n"
            "• Búsqueda de discos y máquinas\n"
            "• Configuración avanzada de hardware y red\n"
            "• Monitoreo en tiempo real\n"
            "• Importación y exportación de configuraciones\n\n"
            "Requisitos:\n"
            "• QEMU instalado en el sistema\n"
            "• PyQt5\n"
            "• Permisos de usuario para QEMU"
        )
        layout.addWidget(description)
        
        layout.addSpacing(20)
        
        copyright_label = QLabel("© 2025 QEMU Manager\nLicencia: GPL v3")
        copyright_label.setStyleSheet("color: gray;")
        layout.addWidget(copyright_label)
        
        layout.addStretch()
        
        ok_btn = QPushButton("Cerrar")
        ok_btn.clicked.connect(self.close)
        layout.addWidget(ok_btn)
        
        self.setLayout(layout)


class SearchDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.found_items = {}
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Buscar Máquinas y Discos")
        self.setGeometry(150, 150, 700, 500)
        
        layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Ruta de búsqueda:"))
        
        self.search_path = QLineEdit()
        self.search_path.setText(str(Path.home()))
        search_layout.addWidget(self.search_path)
        
        browse_btn = QPushButton("Examinar...")
        browse_btn.clicked.connect(self.browse_search_path)
        search_layout.addWidget(browse_btn)
        
        layout.addLayout(search_layout)
        
        options_layout = QHBoxLayout()
        
        self.search_qcow2 = QCheckBox("Buscar .qcow2")
        self.search_qcow2.setChecked(True)
        options_layout.addWidget(self.search_qcow2)
        
        self.search_iso = QCheckBox("Buscar .iso")
        self.search_iso.setChecked(True)
        options_layout.addWidget(self.search_iso)
        
        self.search_img = QCheckBox("Buscar .img")
        self.search_img.setChecked(True)
        options_layout.addWidget(self.search_img)
        
        layout.addLayout(options_layout)
        
        search_btn = QPushButton("Iniciar búsqueda")
        search_btn.clicked.connect(self.start_search)
        layout.addWidget(search_btn)
        
        self.progress = QProgressBar()
        self.progress.setVisible(False)
        layout.addWidget(self.progress)
        
        layout.addWidget(QLabel("Resultados encontrados:"))
        
        self.results_list = QListWidget()
        self.results_list.itemClicked.connect(self.on_item_selected)
        layout.addWidget(self.results_list)
        
        self.file_info = QTextEdit()
        self.file_info.setReadOnly(True)
        self.file_info.setMaximumHeight(150)
        layout.addWidget(self.file_info)
        
        button_layout = QHBoxLayout()
        
        import_btn = QPushButton("Importar Seleccionado")
        import_btn.clicked.connect(self.import_selected)
        button_layout.addWidget(import_btn)
        
        clear_btn = QPushButton("Limpiar Lista")
        clear_btn.clicked.connect(self.results_list.clear)
        button_layout.addWidget(clear_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def browse_search_path(self):
        path = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar directorio de búsqueda",
            self.search_path.text()
        )
        if path:
            self.search_path.setText(path)
    
    def start_search(self):
        self.results_list.clear()
        self.file_info.clear()
        self.found_items = {}
        
        search_path = self.search_path.text()
        if not os.path.exists(search_path):
            QMessageBox.warning(self, "Error", "La ruta no existe")
            return
        
        extensions = []
        if self.search_qcow2.isChecked():
            extensions.append("*.qcow2")
        if self.search_iso.isChecked():
            extensions.append("*.iso")
        if self.search_img.isChecked():
            extensions.append("*.img")
        
        if not extensions:
            QMessageBox.warning(self, "Error", "Seleccione al menos un tipo de archivo")
            return
        
        self.progress.setVisible(True)
        self.progress.setValue(0)
        
        try:
            search_path_obj = Path(search_path)
            found_files = []
            
            for ext in extensions:
                for file_path in search_path_obj.rglob(ext):
                    if file_path.is_file():
                        found_files.append(file_path)
                        self.progress.setValue(min(self.progress.value() + 1, 99))
                        QApplication.processEvents()
            
            self.progress.setValue(100)
            
            for file_path in found_files:
                item_text = f"{file_path.name}"
                self.results_list.addItem(item_text)
                self.found_items[item_text] = str(file_path)
            
            if not found_files:
                QMessageBox.information(self, "Búsqueda", "No se encontraron archivos")
            else:
                QMessageBox.information(self, "Búsqueda", f"Se encontraron {len(found_files)} archivo(s)")
            
            self.progress.setVisible(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error en la búsqueda: {e}")
            self.progress.setVisible(False)
    
    def on_item_selected(self, item):
        file_path = self.found_items.get(item.text())
        if file_path and os.path.exists(file_path):
            try:
                file_size = os.path.getsize(file_path) / (1024**3)
                file_stat = os.stat(file_path)
                from datetime import datetime
                mod_time = datetime.fromtimestamp(file_stat.st_mtime)
                
                info = f"""
                <b>Archivo:</b> {os.path.basename(file_path)}<br>
                <b>Ruta:</b> {file_path}<br>
                <b>Tamaño:</b> {file_size:.2f} GB<br>
                <b>Modificado:</b> {mod_time.strftime('%d/%m/%Y %H:%M:%S')}<br>
                <b>Tipo:</b> {os.path.splitext(file_path)[1].upper()}
                """
                
                if file_path.endswith('.qcow2'):
                    result = subprocess.run(
                        f"qemu-img info '{file_path}' 2>/dev/null",
                        shell=True,
                        capture_output=True,
                        text=True,
                        timeout=5
                    )
                    if result.stdout:
                        info += f"<br><br><b>Información QEMU:</b><pre>{result.stdout}</pre>"
                
                self.file_info.setHtml(info)
            except Exception as e:
                self.file_info.setText(f"Error: {e}")
    
    def import_selected(self):
        item = self.results_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione un archivo")
            return
        
        file_path = self.found_items.get(item.text())
        self.accept()
        return file_path


class QemuGUI(QMainWindow):
    def __init__(self):
        super().__init__()
        self.vms = {}
        self.running_processes = {}
        self.config_file = Path.home() / ".qemu_manager" / "vms.json"
        self.config_file.parent.mkdir(exist_ok=True)
        self.load_existing_vms()
        self.init_ui()
        
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_vm_status)
        self.status_timer.start(2000)

    def load_existing_vms(self):
        """Carga VMs guardadas desde archivo JSON"""
        if self.config_file.exists():
            try:
                with open(self.config_file, 'r') as f:
                    self.vms = json.load(f)
            except Exception as e:
                print(f"Error cargando configuración: {e}")
        
        self.detect_qemu_vms()

    def detect_qemu_vms(self):
        """Detecta máquinas QEMU existentes en el sistema"""
        try:
            home = Path.home()
            for disk_path in home.glob("**/*.qcow2"):
                if disk_path.is_file():
                    disk_name = disk_path.stem
                    if disk_name not in self.vms:
                        self.vms[disk_name] = {
                            "name": disk_name,
                            "disk": str(disk_path),
                            "iso": "",
                            "cpus": 2,
                            "ram": 1024,
                            "os": "Linux",
                            "vga": "qxl",
                            "boot_order": "Disco duro (para arrancar SO)",
                            "auto_detected": True
                        }
            
            common_paths = [
                "/var/lib/libvirt/images",
                os.path.expanduser("~/VirtualMachines"),
                os.path.expanduser("~/QEMU"),
                "/opt/qemu",
            ]
            
            for path_str in common_paths:
                if os.path.exists(path_str):
                    for disk_path in Path(path_str).glob("**/*.qcow2"):
                        if disk_path.is_file():
                            disk_name = disk_path.stem
                            if disk_name not in self.vms:
                                self.vms[disk_name] = {
                                    "name": disk_name,
                                    "disk": str(disk_path),
                                    "iso": "",
                                    "cpus": 2,
                                    "ram": 1024,
                                    "os": "Linux",
                                    "vga": "qxl",
                                    "boot_order": "Disco duro (para arrancar SO)",
                                    "auto_detected": True
                                }
        except Exception as e:
            print(f"Error detectando VMs: {e}")

    def init_ui(self):
        self.setWindowTitle("QEMU Manager - Gestor de Máquinas Virtuales")
        self.setGeometry(100, 100, 1300, 750)
        
        self.create_menu_bar()
        
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)

        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)

        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
        
        self.refresh_vm_list()

    def create_menu_bar(self):
        """Crea la barra de menús"""
        menubar = self.menuBar()
        
        file_menu = menubar.addMenu("Archivo")
        
        new_vm_action = file_menu.addAction("Nueva VM")
        new_vm_action.triggered.connect(self.new_vm)
        new_vm_action.setShortcut("Ctrl+N")
        
        file_menu.addSeparator()
        
        search_action = file_menu.addAction("Buscar Discos/Máquinas")
        search_action.triggered.connect(self.open_search_dialog)
        search_action.setShortcut("Ctrl+F")
        
        file_menu.addSeparator()
        
        load_config_action = file_menu.addAction("Cargar Configuración")
        load_config_action.triggered.connect(self.load_config_file)
        load_config_action.setShortcut("Ctrl+O")
        
        save_config_action = file_menu.addAction("Guardar Configuración")
        save_config_action.triggered.connect(self.save_all_configs)
        save_config_action.setShortcut("Ctrl+S")
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Salir")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        
        edit_menu = menubar.addMenu("Editar")
        
        refresh_action = edit_menu.addAction("Actualizar Lista")
        refresh_action.triggered.connect(self.refresh_vm_list)
        refresh_action.setShortcut("F5")
        
        edit_menu.addSeparator()
        
        import_vm_action = edit_menu.addAction("Importar VM")
        import_vm_action.triggered.connect(self.import_vm)
        
        export_vm_action = edit_menu.addAction("Exportar VM")
        export_vm_action.triggered.connect(self.export_vm)
        
        edit_menu.addSeparator()
        
        delete_vm_action = edit_menu.addAction("Eliminar VM")
        delete_vm_action.triggered.connect(self.delete_vm)
        delete_vm_action.setShortcut("Delete")
        
        tools_menu = menubar.addMenu("Herramientas")

        create_disk_action = tools_menu.addAction("Crear Nuevo Disco")
        create_disk_action.triggered.connect(self.create_new_disk)
        
        tools_menu.addSeparator()
        
        convert_disk_action = tools_menu.addAction("Convertir Formato de Disco")
        convert_disk_action.triggered.connect(self.convert_disk_format)
        
        settings_menu = menubar.addMenu("Configuración")
        settings_action = settings_menu.addAction("Preferencias")
        settings_action.triggered.connect(self.open_settings_dialog)
        settings_action.setShortcut("Ctrl+,")
        
        help_menu = menubar.addMenu("Ayuda")
        
        about_action = help_menu.addAction("Acerca de")
        about_action.triggered.connect(self.show_about)
        
        help_action = help_menu.addAction("Ayuda")
        help_action.triggered.connect(self.show_help)

    def open_settings_dialog(self):
        """Abre el diálogo de configuración"""
        try:
            from qemu_ui.dialogs.settings_dialog import SettingsDialog
            dialog = SettingsDialog(self)
            dialog.exec_()
        except ImportError as e:
            QMessageBox.warning(self, "Error", f"No se pudo cargar el diálogo de configuración: {e}")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error abriendo configuración: {e}")
            
    def open_search_dialog(self):
        """Abre el diálogo de búsqueda"""
        dialog = SearchDialog(self)
        if dialog.exec_() == QDialog.Accepted:
            pass

    def load_config_file(self):
        """Carga una configuración desde archivo"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Cargar Configuración",
            "",
            "JSON Files (*.json);;All Files (*)"
        )
        if path:
            try:
                with open(path, 'r') as f:
                    loaded_vms = json.load(f)
                    self.vms.update(loaded_vms)
                    self.refresh_vm_list()
                    QMessageBox.information(self, "Éxito", "Configuración cargada correctamente")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error cargando configuración: {e}")

    def save_all_configs(self):
        """Guarda todas las configuraciones en un archivo"""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Guardar Configuración",
            "qemu_config.json",
            "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, 'w') as f:
                    json.dump(self.vms, f, indent=2)
                QMessageBox.information(self, "Éxito", "Configuración guardada")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error guardando: {e}")

    def import_vm(self):
        """Importa una VM desde archivo"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Importar VM",
            "",
            "QEMU Image (*.qcow2);;Imagen (*.img);;Disco (*.vdi)"
        )
        if path:
            vm_name = Path(path).stem
            self.vms[vm_name] = {
                "name": vm_name,
                "disk": path,
                "iso": "",
                "cpus": 2,
                "ram": 1024,
                "os": "Linux",
                "vga": "qxl",
                "boot_order": "Disco duro (para arrancar SO)",
                "auto_detected": False
            }
            self.refresh_vm_list()
            QMessageBox.information(self, "Éxito", f"VM '{vm_name}' importada")

    def export_vm(self):
        """Exporta la configuración de una VM"""
        item = self.vm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una VM")
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        config = self.vms.get(vm_name)
        
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Exportar VM",
            f"{vm_name}.json",
            "JSON Files (*.json)"
        )
        if path:
            try:
                with open(path, 'w') as f:
                    json.dump({vm_name: config}, f, indent=2)
                QMessageBox.information(self, "Éxito", "VM exportada")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error exportando: {e}")

    def create_new_disk(self):
        """Crea un nuevo disco QEMU"""
        path, _ = QFileDialog.getSaveFileName(
            self,
            "Crear Nuevo Disco",
            "",
            "QCOW2 (*.qcow2)"
        )
        if path:
            size, ok = self._get_disk_size()
            if ok and size > 0:
                try:
                    cmd = f"qemu-img create -f qcow2 \"{path}\" {size}G"
                    subprocess.run(cmd, shell=True, check=True, capture_output=True)
                    QMessageBox.information(self, "Éxito", f"Disco creado: {size}GB")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error creando disco: {e}")

    def _get_disk_size(self):
        """Obtiene el tamaño del disco del usuario"""
        dialog = QDialog(self)
        dialog.setWindowTitle("Tamaño del Disco")
        layout = QVBoxLayout()
        
        layout.addWidget(QLabel("Tamaño en GB:"))
        size_input = QSpinBox()
        size_input.setRange(1, 2000)
        size_input.setValue(20)
        layout.addWidget(size_input)
        
        btn_layout = QHBoxLayout()
        ok_btn = QPushButton("OK")
        cancel_btn = QPushButton("Cancelar")
        ok_btn.clicked.connect(dialog.accept)
        cancel_btn.clicked.connect(dialog.reject)
        btn_layout.addWidget(ok_btn)
        btn_layout.addWidget(cancel_btn)
        
        layout.addLayout(btn_layout)
        dialog.setLayout(layout)
        
        ok = dialog.exec_() == QDialog.Accepted
        return size_input.value(), ok

    def convert_disk_format(self):
        """Convierte el formato de un disco"""
        path, _ = QFileDialog.getOpenFileName(
            self,
            "Seleccionar Disco",
            "",
            "All Files (*)"
        )
        if path:
            new_path, _ = QFileDialog.getSaveFileName(
                self,
                "Guardar Como",
                "",
                "QCOW2 (*.qcow2);;RAW (*.img)"
            )
            if new_path:
                format_type = "qcow2" if new_path.endswith(".qcow2") else "raw"
                try:
                    cmd = f"qemu-img convert -f auto -O {format_type} \"{path}\" \"{new_path}\""
                    subprocess.run(cmd, shell=True, check=True, capture_output=True)
                    QMessageBox.information(self, "Éxito", "Disco convertido")
                except Exception as e:
                    QMessageBox.critical(self, "Error", f"Error: {e}")

    def show_about(self):
        """Muestra el diálogo About"""
        dialog = AboutDialog(self)
        dialog.exec_()

    def show_help(self):
        """Muestra la ayuda"""
        help_text = """
        <b>QEMU Manager - Ayuda</b><br><br>
        
        <b>Funcionalidades:</b><br>
        • <b>Nueva VM:</b> Crear una nueva máquina virtual<br>
        • <b>Buscar:</b> Buscar discos e imágenes existentes<br>
        • <b>Importar:</b> Importar discos existentes<br>
        • <b>Exportar:</b> Exportar configuración de VM<br>
        • <b>Iniciar/Detener:</b> Controlar máquinas virtuales<br><br>
        
        <b>Atajos de teclado:</b><br>
        • Ctrl+N: Nueva VM<br>
        • Ctrl+F: Buscar<br>
        • Ctrl+O: Cargar configuración<br>
        • Ctrl+S: Guardar configuración<br>
        • F5: Actualizar lista<br>
        • Ctrl+Q: Salir<br><br>
        
        <b>Requisitos:</b><br>
        • QEMU instalado<br>
        • Permisos de usuario<br>
        • qemu-img para crear/convertir discos
        """
        
        dialog = QDialog(self)
        dialog.setWindowTitle("Ayuda")
        dialog.setGeometry(200, 200, 600, 400)
        layout = QVBoxLayout()
        
        text = QTextEdit()
        text.setHtml(help_text)
        text.setReadOnly(True)
        layout.addWidget(text)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(dialog.close)
        layout.addWidget(close_btn)
        
        dialog.setLayout(layout)
        dialog.exec_()

    def create_left_panel(self):
        group = QGroupBox("Máquinas Virtuales")
        layout = QVBoxLayout()

        self.info_label = QLabel("Cargando máquinas virtuales...")
        layout.addWidget(self.info_label)

        self.vm_list = QListWidget()
        self.vm_list.itemClicked.connect(self.on_vm_selected)
        layout.addWidget(self.vm_list)

        btn_layout = QVBoxLayout()
        
        btn_refresh = QPushButton("Actualizar Lista")
        btn_refresh.clicked.connect(self.refresh_vm_list)
        btn_layout.addWidget(btn_refresh)
        
        btn_new = QPushButton("Nueva VM")
        btn_new.clicked.connect(self.new_vm)
        btn_layout.addWidget(btn_new)

        btn_delete = QPushButton("Eliminar VM")
        btn_delete.clicked.connect(self.delete_vm)
        btn_layout.addWidget(btn_delete)

        start_stop_layout = QHBoxLayout()
        btn_start = QPushButton("Iniciar")
        btn_start.clicked.connect(self.start_vm)
        start_stop_layout.addWidget(btn_start)

        btn_stop = QPushButton("Detener")
        btn_stop.clicked.connect(self.stop_vm)
        start_stop_layout.addWidget(btn_stop)
        
        btn_layout.addLayout(start_stop_layout)

        restart_shutdown_layout = QHBoxLayout()
        btn_restart = QPushButton("Reiniciar")
        btn_restart.clicked.connect(self.restart_vm)
        restart_shutdown_layout.addWidget(btn_restart)

        btn_shutdown = QPushButton("Apagar")
        btn_shutdown.clicked.connect(self.shutdown_vm)
        restart_shutdown_layout.addWidget(btn_shutdown)
        
        btn_layout.addLayout(restart_shutdown_layout)

        btn_save = QPushButton("Guardar Configuración")
        btn_save.clicked.connect(self.save_config)
        btn_layout.addWidget(btn_save)

        layout.addLayout(btn_layout)
        group.setLayout(layout)
        return group

    def create_right_panel(self):
        self.tabs = QTabWidget()

        config_tab = self.create_config_tab()
        self.tabs.addTab(config_tab, "Configuración")

        hardware_tab = self.create_hardware_tab()
        self.tabs.addTab(hardware_tab, "Hardware")

        network_tab = self.create_network_tab()
        self.tabs.addTab(network_tab, "Red")

        info_tab = self.create_info_tab()
        self.tabs.addTab(info_tab, "Información")

        return self.tabs

    def create_config_tab(self):
        widget = QWidget()
        layout = QFormLayout()

        self.name_input = QLineEdit()
        layout.addRow("Nombre VM:", self.name_input)

        self.iso_path = QLineEdit()
        btn_browse_iso = QPushButton("Examinar...")
        btn_browse_iso.clicked.connect(self.browse_iso)
        iso_layout = QHBoxLayout()
        iso_layout.addWidget(self.iso_path)
        iso_layout.addWidget(btn_browse_iso)
        layout.addRow("Imagen ISO:", iso_layout)

        self.disk_path = QLineEdit()
        btn_browse_disk = QPushButton("Examinar...")
        btn_browse_disk.clicked.connect(self.browse_disk)
        disk_layout = QHBoxLayout()
        disk_layout.addWidget(self.disk_path)
        disk_layout.addWidget(btn_browse_disk)
        layout.addRow("Disco Duro:", disk_layout)

        self.os_type = QComboBox()
        self.os_type.addItems(["Linux", "Windows", "macOS", "Otro"])
        layout.addRow("Sistema Operativo:", self.os_type)

        self.auto_detect_label = QLabel("")
        layout.addRow("Estado:", self.auto_detect_label)

        widget.setLayout(layout)
        return widget

    def create_hardware_tab(self):
        widget = QWidget()
        layout = QFormLayout()

        self.cpu_cores = QSpinBox()
        self.cpu_cores.setValue(2)
        self.cpu_cores.setRange(1, 16)
        layout.addRow("Núcleos CPU:", self.cpu_cores)

        self.ram_size = QSpinBox()
        self.ram_size.setValue(1024)
        self.ram_size.setRange(256, 16384)
        self.ram_size.setSuffix(" MB")
        layout.addRow("Memoria RAM:", self.ram_size)

        self.vga_type = QComboBox()
        self.vga_type.addItems(["qxl", "virtio", "vmware", "vga"])
        layout.addRow("Tipo VGA:", self.vga_type)

        self.boot_order = QComboBox()
        self.boot_order.addItems([
            "Disco duro (para arrancar SO)",
            "CD/DVD primero (para instalar)"
        ])
        layout.addRow("Orden de Boot:", self.boot_order)

        self.enable_kvm = QCheckBox("Habilitar KVM (aceleración)")
        self.enable_kvm.setChecked(True)
        layout.addRow("Aceleración:", self.enable_kvm)

        widget.setLayout(layout)
        return widget

    def create_network_tab(self):
        widget = QWidget()
        layout = QFormLayout()

        self.net_model = QComboBox()
        self.net_model.addItems(["virtio", "e1000", "rtl8139"])
        layout.addRow("Modelo Red:", self.net_model)

        self.net_type = QComboBox()
        self.net_type.addItems(["user", "bridge", "tap"])
        layout.addRow("Tipo Conexión:", self.net_type)

        self.net_interface = QLineEdit()
        self.net_interface.setText("br0")
        layout.addRow("Interfaz:", self.net_interface)

        self.enable_slirp = QCheckBox("Usar SLIRP")
        layout.addRow("SLIRP:", self.enable_slirp)

        widget.setLayout(layout)
        return widget

    def create_info_tab(self):
        widget = QWidget()
        layout = QVBoxLayout()

        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)

        widget.setLayout(layout)
        return widget

    def browse_iso(self):
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar ISO", "", "ISO Files (*.iso)")
        if path:
            self.iso_path.setText(path)

    def browse_disk(self):
        path, _ = QFileDialog.getSaveFileName(self, "Seleccionar Disco", "", "QEMU Image (*.qcow2)")
        if path:
            self.disk_path.setText(path)

    def refresh_vm_list(self):
        """Actualiza la lista de VMs en la interfaz"""
        self.vm_list.clear()
        
        for vm_name in sorted(self.vms.keys()):
            item = QListWidgetItem(vm_name)
            config = self.vms[vm_name]
            
            if config.get("auto_detected"):
                item.setText(f"📦 {vm_name} (detectada)")
                item.setForeground(QColor("blue"))
            else:
                item.setText(f"⚙️ {vm_name}")
            
            if vm_name in self.running_processes:
                item.setText(item.text() + " [EJECUTANDO]")
                item.setBackground(QColor("lightgreen"))
            
            self.vm_list.addItem(item)
        
        self.info_label.setText(f"Total de VMs: {len(self.vms)}")

    def on_vm_selected(self, item):
        """Carga la configuración de una VM seleccionada"""
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").replace(" [EJECUTANDO]", "")
        vm_name = vm_name.split("[")[0].strip()
        
        if vm_name in self.vms:
            config = self.vms[vm_name]
            self.name_input.setText(config.get("name", ""))
            self.iso_path.setText(config.get("iso", ""))
            self.disk_path.setText(config.get("disk", ""))
            self.cpu_cores.setValue(config.get("cpus", 2))
            self.ram_size.setValue(config.get("ram", 1024))
            self.os_type.setCurrentText(config.get("os", "Linux"))
            self.vga_type.setCurrentText(config.get("vga", "qxl"))
            self.boot_order.setCurrentText(config.get("boot_order", "Disco duro (para arrancar SO)"))
            
            if config.get("auto_detected"):
                self.auto_detect_label.setText("✓ Auto-detectada del sistema")
            else:
                self.auto_detect_label.setText("✓ Configuración manual")
            
            self.show_vm_info(vm_name, config)

    def show_vm_info(self, vm_name, config):
        """Muestra información detallada de la VM"""
        info = f"""
        <b>Información de la Máquina Virtual</b><br><br>
        <b>Nombre:</b> {config.get('name', 'N/A')}<br>
        <b>Estado:</b> {'🟢 En ejecución' if vm_name in self.running_processes else '🔴 Detenida'}<br><br>
        
        <b>Configuración:</b><br>
        • <b>CPU:</b> {config.get('cpus', 'N/A')} núcleos<br>
        • <b>RAM:</b> {config.get('ram', 'N/A')} MB<br>
        • <b>SO:</b> {config.get('os', 'N/A')}<br><br>
        
        <b>Almacenamiento:</b><br>
        • <b>Disco:</b> {config.get('disk', 'No configurado')}<br>
        • <b>ISO:</b> {config.get('iso', 'No configurado')}<br><br>
        
        <b>Información del Disco:</b><br>
        """
        
        disk_path = config.get("disk")
        if disk_path and os.path.exists(disk_path):
            try:
                result = subprocess.run(
                    f"qemu-img info '{disk_path}' 2>/dev/null || ls -lh '{disk_path}'",
                    shell=True,
                    capture_output=True,
                    text=True,
                    timeout=5
                )
                if result.stdout:
                    info += f"<pre>{result.stdout}</pre>"
                else:
                    file_size = os.path.getsize(disk_path) / (1024**3)
                    info += f"• Tamaño: {file_size:.2f} GB<br>"
            except Exception as e:
                info += f"• Error obteniendo info: {str(e)}<br>"
        
        self.info_text.setHtml(info)

    def new_vm(self):
        """Crea una nueva VM"""
        self.name_input.clear()
        self.iso_path.clear()
        self.disk_path.clear()
        self.cpu_cores.setValue(2)
        self.ram_size.setValue(1024)
        self.vga_type.setCurrentText("qxl")
        self.boot_order.setCurrentText("Disco duro (para arrancar SO)")
        self.auto_detect_label.setText("")
        self.vm_list.clearSelection()

    def save_config(self):
        """Guarda la configuración de la VM"""
        name = self.name_input.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Ingrese un nombre para la VM")
            return

        self.vms[name] = {
            "name": name,
            "iso": self.iso_path.text(),
            "disk": self.disk_path.text(),
            "cpus": self.cpu_cores.value(),
            "ram": self.ram_size.value(),
            "os": self.os_type.currentText(),
            "vga": self.vga_type.currentText(),
            "boot_order": self.boot_order.currentText(),
            "auto_detected": False
        }
        
        try:
            with open(self.config_file, 'w') as f:
                json.dump(self.vms, f, indent=2)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando configuración: {e}")
            return
        
        self.refresh_vm_list()
        QMessageBox.information(self, "Éxito", f"Configuración de '{name}' guardada")

    def start_vm(self):
        """Inicia una VM"""
        item = self.vm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una VM")
            return

        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        config = self.vms.get(vm_name)
        
        if not config:
            QMessageBox.warning(self, "Error", "Configuración no encontrada")
            return
        
        if vm_name in self.running_processes:
            QMessageBox.warning(self, "Advertencia", f"La VM '{vm_name}' ya está en ejecución")
            return

        cmd = self.build_qemu_command(config)
        try:
            env = os.environ.copy()
            self.running_processes[vm_name] = subprocess.Popen(cmd, shell=True, env=env)
            self.refresh_vm_list()
            QMessageBox.information(self, "Éxito", f"VM '{vm_name}' iniciada")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error iniciando VM: {e}")

    def stop_vm(self):
        """Detiene una VM"""
        item = self.vm_list.currentItem()
        if not item:
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        
        if vm_name in self.running_processes:
            try:
                self.running_processes[vm_name].terminate()
                self.running_processes[vm_name].wait(timeout=5)
            except:
                self.running_processes[vm_name].kill()
            
            del self.running_processes[vm_name]
            self.refresh_vm_list()
            QMessageBox.information(self, "Éxito", f"VM '{vm_name}' detenida")
        else:
            QMessageBox.warning(self, "Advertencia", f"La VM '{vm_name}' no está en ejecución")

    def restart_vm(self):
        """Reinicia VM seleccionada"""
        item = self.vm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una VM")
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        
        try:
            if vm_name not in self.running_processes:
                QMessageBox.warning(self, "Advertencia", f"La VM '{vm_name}' no está en ejecución")
                return
            
            if self.running_processes[vm_name]:
                self.running_processes[vm_name].terminate()
                self.running_processes[vm_name].wait(timeout=5)
            
            del self.running_processes[vm_name]
            self.refresh_vm_list()
            
            from time import sleep
            sleep(1)
            
            config = self.vms.get(vm_name)
            if config:
                cmd = self.build_qemu_command(config)
                env = os.environ.copy()
                self.running_processes[vm_name] = subprocess.Popen(cmd, shell=True, env=env)
                self.refresh_vm_list()
                QMessageBox.information(self, "Éxito", f"VM '{vm_name}' reiniciada")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reiniciando VM: {e}")

    def shutdown_vm(self):
        """Apaga VM seleccionada"""
        item = self.vm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una VM")
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        
        try:
            if vm_name not in self.running_processes:
                QMessageBox.warning(self, "Advertencia", f"La VM '{vm_name}' no está en ejecución")
                return
            
            reply = QMessageBox.question(
                self,
                "Confirmar apagado",
                f"¿Apagar la VM '{vm_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                if self.running_processes[vm_name]:
                    self.running_processes[vm_name].terminate()
                    self.running_processes[vm_name].wait(timeout=5)
                
                del self.running_processes[vm_name]
                self.refresh_vm_list()
                QMessageBox.information(self, "Éxito", f"VM '{vm_name}' apagada")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error apagando VM: {e}")

    def delete_vm(self):
        """Elimina una VM"""
        item = self.vm_list.currentItem()
        if not item:
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        
        reply = QMessageBox.question(
            self, 
            "Confirmar", 
            f"¿Eliminar la VM '{vm_name}'?\n(No se eliminarán los archivos de disco)",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            del self.vms[vm_name]
            try:
                with open(self.config_file, 'w') as f:
                    json.dump(self.vms, f, indent=2)
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error guardando: {e}")
            
            self.refresh_vm_list()

    def update_vm_status(self):
        """Actualiza el estado de las VMs en ejecución"""
        dead_vms = []
        for vm_name, process in self.running_processes.items():
            if process.poll() is not None:
                dead_vms.append(vm_name)
        
        for vm_name in dead_vms:
            del self.running_processes[vm_name]
            self.refresh_vm_list()

    def build_qemu_command(self, config):
        """Construye el comando de QEMU con soporte de entrada y display"""
        cmd = "qemu-system-x86_64"
        cmd += f" -name {config['name']}"
        cmd += f" -m {config['ram']}"
        cmd += f" -smp cores={config['cpus']}"

        if config.get("iso"):
            cmd += f' -cdrom "{config["iso"]}"'
        if config.get("disk"):
            cmd += f' -hda "{config["disk"]}"'

        boot_order = config.get("boot_order", "Disco duro (para arrancar SO)")
        if "Disco duro" in boot_order:
            cmd += " -boot order=c,d,menu=on"
        else:
            cmd += " -boot order=d,c,menu=on"

        cmd += " -usb"
        cmd += " -device usb-kbd"
        cmd += " -device usb-mouse"

        vga = config.get("vga", "qxl")
        cmd += f" -vga {vga}"

        # Configurar display para mostrar la ventana
        if sys.platform == 'win32':
            cmd += " -accel whpx"
            cmd += " -display sdl"
        elif sys.platform == 'darwin':
            cmd += " -accel hvf"
            cmd += " -display cocoa"
        else:
            cmd += " -enable-kvm"
            cmd += " -display gtk,gl=on"

        cmd += " -net nic,model=virtio"
        cmd += " -net user"

        cmd += " -audiodev sdl,id=audio0"
        cmd += " -device intel-hda"
        cmd += " -device hda-duplex,audiodev=audio0"

        print(f"[DEBUG] Comando QEMU: {cmd}")
        return cmd

    def closeEvent(self, event):
        """Detiene todas las VMs al cerrar la aplicación"""
        for process in self.running_processes.values():
            try:
                process.terminate()
            except:
                pass
        event.accept()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    gui = QemuGUI()
    gui.show()
    sys.exit(app.exec_())