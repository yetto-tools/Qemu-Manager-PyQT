# qemu_ui/dialogs/disk_manager_dialog.py
"""
Diálogo para gestionar discos virtuales - CON LOADING OVERLAY
"""

from qemu_ui.widgets import LoadingOverlay
from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QSpinBox, QComboBox, QTableWidget, QTableWidgetItem,
    QFileDialog, QMessageBox, QCheckBox, QFormLayout, QProgressBar, QWidget
)
from PyQt5.QtCore import Qt, QThread, pyqtSignal
from pathlib import Path
import os


class DiskSearchWorker(QThread):
    """Worker thread para buscar discos sin bloquear la UI"""
    
    progress = pyqtSignal(str)
    finished = pyqtSignal(list)
    
    def __init__(self, search_paths):
        super().__init__()
        self.search_paths = search_paths
        self.disks = []
    
    def run(self):
        """Busca discos en background"""
        for path_str in self.search_paths:
            if not os.path.exists(path_str):
                continue
            
            try:
                path_obj = Path(path_str)
                
                # Limitar profundidad de búsqueda a 3 niveles
                for disk_path in self._walk_limited(path_obj, max_depth=3):
                    if disk_path.suffix in ['.qcow2', '.img', '.vdi', '.vmdk']:
                        self.disks.append(disk_path)
                        self.progress.emit(f"Encontrado: {disk_path.name}")
            except Exception as e:
                print(f"Error buscando en {path_str}: {e}")
        
        self.finished.emit(self.disks)
    
    def _walk_limited(self, path, max_depth=3, current_depth=0):
        """Recorre directorios limitando profundidad"""
        if current_depth >= max_depth:
            return
        
        try:
            for item in path.iterdir():
                if item.is_file():
                    yield item
                elif item.is_dir() and not item.name.startswith('.'):
                    yield from self._walk_limited(item, max_depth, current_depth + 1)
        except (PermissionError, OSError):
            pass


class DiskManagerDialog(QDialog):
    """Diálogo para gestionar discos virtuales"""
    
    def __init__(self, parent=None, storage_adapter=None):
        super().__init__(parent)
        self.storage = storage_adapter
        self.search_worker = None
        self.loading_overlay = None
        self.disks_found = []
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Gestor de Discos Virtuales")
        self.setGeometry(100, 100, 900, 600)
        
        layout = QVBoxLayout()
        
        from PyQt5.QtWidgets import QTabWidget
        self.tabs = QTabWidget()
        
        create_tab = self.create_disk_tab()
        self.tabs.addTab(create_tab, "Crear Disco")
        
        manage_tab = self.manage_disks_tab()
        self.tabs.addTab(manage_tab, "Gestionar Discos")
        
        convert_tab = self.convert_disk_tab()
        self.tabs.addTab(convert_tab, "Convertir Formato")
        
        layout.addWidget(self.tabs)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def create_disk_tab(self):
        """Pestaña para crear nuevo disco"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.disk_name = QLineEdit()
        layout.addRow("Nombre del Disco:", self.disk_name)
        
        self.disk_location = QLineEdit()
        self.disk_location.setText(str(Path.home() / "VirtualMachines"))
        btn_browse = QPushButton("Examinar...")
        btn_browse.clicked.connect(self.browse_disk_location)
        loc_layout = QHBoxLayout()
        loc_layout.addWidget(self.disk_location)
        loc_layout.addWidget(btn_browse)
        layout.addRow("Ubicacion:", loc_layout)
        
        size_layout = QHBoxLayout()
        self.disk_size = QSpinBox()
        self.disk_size.setRange(1, 2000)
        self.disk_size.setValue(20)
        size_layout.addWidget(self.disk_size)
        size_layout.addWidget(QLabel("GB"))
        layout.addRow("Tamano:", size_layout)
        
        self.disk_format = QComboBox()
        self.disk_format.addItems(["qcow2", "raw", "vdi", "vmdk"])
        layout.addRow("Formato:", self.disk_format)
        
        self.disk_preset = QComboBox()
        self.disk_preset.addItems(["Personalizado", "Linux (20GB)", "Windows (50GB)", "Servidor (100GB)"])
        self.disk_preset.currentTextChanged.connect(self.on_preset_changed)
        layout.addRow("Preconfiguracion:", self.disk_preset)
        
        self.disk_progress = QProgressBar()
        self.disk_progress.setVisible(False)
        layout.addRow("Progreso:", self.disk_progress)
        
        btn_create = QPushButton("[CREATE] Crear Disco")
        btn_create.clicked.connect(self.create_disk)
        layout.addRow("", btn_create)
        
        widget.setLayout(layout)
        return widget
    
    def manage_disks_tab(self):
        """Pestaña para gestionar discos existentes"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        # Tabla de discos
        self.disks_table = QTableWidget()
        self.disks_table.setColumnCount(5)
        self.disks_table.setHorizontalHeaderLabels(["Nombre", "Tamano", "Ubicacion", "Formato", "Acciones"])
        self.disks_table.setColumnWidth(2, 300)
        layout.addWidget(self.disks_table)
        
        # Botón actualizar
        btn_refresh = QPushButton("[REFRESH] Actualizar Lista")
        btn_refresh.clicked.connect(self.refresh_disks)
        layout.addWidget(btn_refresh)
        
        widget.setLayout(layout)
        
        # Crear overlay de carga (inicialmente oculto)
        self.loading_overlay = LoadingOverlay(widget)
        self.loading_overlay.hide()
        
        # Iniciar búsqueda en background
        self.refresh_disks()
        
        return widget
    
    def convert_disk_tab(self):
        """Pestaña para convertir formato de disco"""
        widget = QWidget()
        layout = QFormLayout()
        
        self.conv_source = QLineEdit()
        btn_browse_source = QPushButton("Examinar...")
        btn_browse_source.clicked.connect(lambda: self.browse_file(self.conv_source))
        source_layout = QHBoxLayout()
        source_layout.addWidget(self.conv_source)
        source_layout.addWidget(btn_browse_source)
        layout.addRow("Disco de Origen:", source_layout)
        
        self.conv_format = QComboBox()
        self.conv_format.addItems(["qcow2", "raw", "vdi", "vmdk"])
        layout.addRow("Formato Destino:", self.conv_format)
        
        self.conv_dest = QLineEdit()
        btn_browse_dest = QPushButton("Examinar...")
        btn_browse_dest.clicked.connect(lambda: self.browse_file(self.conv_dest, save=True))
        dest_layout = QHBoxLayout()
        dest_layout.addWidget(self.conv_dest)
        dest_layout.addWidget(btn_browse_dest)
        layout.addRow("Archivo Destino:", dest_layout)
        
        self.conv_progress = QProgressBar()
        self.conv_progress.setVisible(False)
        layout.addRow("Progreso:", self.conv_progress)
        
        btn_convert = QPushButton("[CONVERT] Convertir Disco")
        btn_convert.clicked.connect(self.convert_disk)
        layout.addRow("", btn_convert)
        
        widget.setLayout(layout)
        return widget
    
    def browse_disk_location(self):
        """Abre dialogo para seleccionar ubicación"""
        path = QFileDialog.getExistingDirectory(self, "Seleccionar ubicacion")
        if path:
            self.disk_location.setText(path)
    
    def browse_file(self, line_edit, save=False):
        """Abre dialogo para seleccionar archivo"""
        if save:
            path, _ = QFileDialog.getSaveFileName(self, "Guardar como")
        else:
            path, _ = QFileDialog.getOpenFileName(self, "Seleccionar archivo")
        if path:
            line_edit.setText(path)
    
    def on_preset_changed(self, text):
        """Maneja cambio de preconfiguracion"""
        if "Linux" in text:
            self.disk_size.setValue(20)
            self.disk_format.setCurrentText("qcow2")
        elif "Windows" in text:
            self.disk_size.setValue(50)
            self.disk_format.setCurrentText("qcow2")
        elif "Servidor" in text:
            self.disk_size.setValue(100)
            self.disk_format.setCurrentText("qcow2")
    
    def create_disk(self):
        """Crea nuevo disco virtual"""
        name = self.disk_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Ingrese un nombre")
            return
        
        location = self.disk_location.text()
        size = self.disk_size.value()
        format_type = self.disk_format.currentText()
        
        Path(location).mkdir(parents=True, exist_ok=True)
        disk_path = str(Path(location) / f"{name}.{format_type}")
        
        try:
            self.disk_progress.setVisible(True)
            if self.storage.create_disk(disk_path, size, format_type):
                self.disk_progress.setValue(100)
                QMessageBox.information(self, "Exito", f"Disco creado: {size}GB")
                self.disk_name.clear()
                self.refresh_disks()
            else:
                QMessageBox.critical(self, "Error", "No se pudo crear el disco")
            self.disk_progress.setVisible(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.disk_progress.setVisible(False)
    
    def refresh_disks(self):
        """Actualiza lista de discos en background"""
        # Mostrar loading overlay
        if self.loading_overlay:
            self.loading_overlay.show()
            self.loading_overlay.update_message(
                "Escaneando discos...",
                "Buscando archivos QCOW2, IMG, VDI y VMDK"
            )
        
        # Detener búsqueda anterior si está en curso
        if self.search_worker and self.search_worker.isRunning():
            self.search_worker.wait()
        
        # Definir rutas de búsqueda limitadas
        search_paths = [
            str(Path.home() / "VirtualMachines"),
            str(Path.home() / "QEMU"),
            str(Path.home() / "Documentos"),
        ]
        
        # Crear worker para búsqueda en background
        self.search_worker = DiskSearchWorker(search_paths)
        self.search_worker.progress.connect(self.update_loading_progress)
        self.search_worker.finished.connect(self.on_disks_found)
        self.search_worker.start()
    
    def update_loading_progress(self, message):
        """Actualiza etiqueta de estado del loading"""
        if self.loading_overlay:
            self.loading_overlay.update_message(
                "Escaneando discos...",
                message
            )
    
    def on_disks_found(self, disks):
        """Cuando se completó la búsqueda de discos"""
        # Ocultar loading overlay
        if self.loading_overlay:
            self.loading_overlay.stop()
            self.loading_overlay.hide()
        
        # Guardar discos encontrados
        self.disks_found = disks
        
        # Llenar tabla
        self.disks_table.setRowCount(0)
        
        for disk_path in disks:
            self.add_disk_row(disk_path)
    
    def add_disk_row(self, disk_path):
        """Agrega fila de disco a tabla"""
        row = self.disks_table.rowCount()
        self.disks_table.insertRow(row)
        
        name = disk_path.stem
        size_gb = disk_path.stat().st_size / (1024**3)
        location = str(disk_path.parent)
        format_type = disk_path.suffix[1:]
        
        self.disks_table.setItem(row, 0, QTableWidgetItem(name))
        self.disks_table.setItem(row, 1, QTableWidgetItem(f"{size_gb:.2f} GB"))
        self.disks_table.setItem(row, 2, QTableWidgetItem(location))
        self.disks_table.setItem(row, 3, QTableWidgetItem(format_type.upper()))
        
        btn_delete = QPushButton("[DELETE]")
        btn_delete.clicked.connect(lambda: self.delete_disk(str(disk_path)))
        self.disks_table.setCellWidget(row, 4, btn_delete)
    
    def delete_disk(self, disk_path):
        """Elimina disco"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            f"Eliminar disco?\n{disk_path}",
            QMessageBox.Yes | QMessageBox.No
        )
        if reply == QMessageBox.Yes:
            if self.storage.delete_disk(disk_path):
                QMessageBox.information(self, "Exito", "Disco eliminado")
                self.refresh_disks()
            else:
                QMessageBox.critical(self, "Error", "No se pudo eliminar")
    
    def convert_disk(self):
        """Convierte formato de disco"""
        source = self.conv_source.text().strip()
        if not source:
            QMessageBox.warning(self, "Error", "Seleccione disco origen")
            return
        
        dest = self.conv_dest.text().strip()
        if not dest:
            QMessageBox.warning(self, "Error", "Especifique destino")
            return
        
        format_type = self.conv_format.currentText()
        
        try:
            self.conv_progress.setVisible(True)
            if self.storage.convert_disk(source, dest, format_type):
                self.conv_progress.setValue(100)
                QMessageBox.information(self, "Exito", f"Convertido a {format_type}")
            else:
                QMessageBox.critical(self, "Error", "No se pudo convertir")
            self.conv_progress.setVisible(False)
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))
            self.conv_progress.setVisible(False)