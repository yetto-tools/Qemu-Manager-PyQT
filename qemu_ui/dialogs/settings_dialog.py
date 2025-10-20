# qemu_ui/dialogs/settings_dialog.py

"""
Diálogo de configuración de la aplicación
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QTabWidget, QWidget,
    QFormLayout, QComboBox, QSpinBox, QLineEdit, QPushButton,
    QLabel, QMessageBox, QFileDialog
)
from PyQt5.QtCore import Qt

# Importar el gestor de configuración
try:
    from qemu_adapters.config_manager import get_config
except ImportError:
    # Si no existe aún, usar valores dummy
    def get_config():
        class DummyConfig:
            CONFIG_FILE = "config.json"
            def get_acceleration_type(self): return "whpx"
            def set_acceleration_type(self, x): pass
            def get_vm_defaults(self): return {"cpus": 2, "ram": 1024, "vga": "qxl"}
            def set_vm_defaults(self, x): pass
            def get_iso_dir(self): return "."
            def set_iso_dir(self, x): pass
            def get_disk_dir(self): return "."
            def set_disk_dir(self, x): pass
            def get_theme(self): return "light"
            def set_theme(self, x): pass
            def save_config(self): return True
        return DummyConfig()


class SettingsDialog(QDialog):
    """Diálogo para cambiar configuración de la aplicación"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.config = get_config()
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Configuración - QEMU Manager")
        self.setGeometry(200, 200, 600, 500)
        
        layout = QVBoxLayout()
        
        # Tabs
        tabs = QTabWidget()
        
        # Tab: Hardware
        hardware_tab = self.create_hardware_tab()
        tabs.addTab(hardware_tab, "Hardware")
        
        # Tab: Directorios
        paths_tab = self.create_paths_tab()
        tabs.addTab(paths_tab, "Directorios")
        
        # Tab: Interfaz
        ui_tab = self.create_ui_tab()
        tabs.addTab(ui_tab, "Interfaz")
        
        layout.addWidget(tabs)
        
        # Botones
        button_layout = QHBoxLayout()
        
        save_btn = QPushButton("Guardar")
        save_btn.clicked.connect(self.save_settings)
        button_layout.addWidget(save_btn)
        
        reset_btn = QPushButton("Restaurar Defaults")
        reset_btn.clicked.connect(self.reset_defaults)
        button_layout.addWidget(reset_btn)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        button_layout.addWidget(close_btn)
        
        layout.addLayout(button_layout)
        
        self.setLayout(layout)
    
    def create_hardware_tab(self):
        """Crea la pestaña de hardware"""
        widget = QWidget()
        main_layout = QVBoxLayout()
        
        # Aceleración
        title1 = QLabel("<b>Aceleración de Hardware</b>")
        main_layout.addWidget(title1)
        
        form1 = QFormLayout()
        
        self.accel_combo = QComboBox()
        accel_options = [
            ("Ninguna (Más lento)", "none"),
            ("KVM (Linux)", "kvm"),
            ("WHPX (Windows 11)", "whpx"),
            ("HAX (Intel)", "hax"),
            ("TCG (Genérico)", "tcg")
        ]
        
        for text, value in accel_options:
            self.accel_combo.addItem(text, value)
        
        # Seleccionar el tipo actual
        current_accel = self.config.get_acceleration_type()
        for i in range(self.accel_combo.count()):
            if self.accel_combo.itemData(i) == current_accel:
                self.accel_combo.setCurrentIndex(i)
                break
        
        form1.addRow("Tipo de Aceleración:", self.accel_combo)
        
        accel_info = QLabel(
            "<small>• <b>Ninguna:</b> Emulación pura (más lento, compatible)<br>"
            "• <b>KVM:</b> Mejor para Linux<br>"
            "• <b>WHPX:</b> Recomendado para Windows 11<br>"
            "• <b>HAX:</b> Para procesadores Intel en Windows/macOS<br>"
            "• <b>TCG:</b> Emulador genérico</small>"
        )
        accel_info.setWordWrap(True)
        form1.addRow("", accel_info)
        
        main_layout.addLayout(form1)
        main_layout.addSpacing(20)
        
        # Valores por defecto para VMs
        title2 = QLabel("<b>Valores por Defecto para Nuevas VMs</b>")
        main_layout.addWidget(title2)
        
        form2 = QFormLayout()
        
        vm_defaults = self.config.get_vm_defaults()
        
        self.cpu_spin = QSpinBox()
        self.cpu_spin.setValue(vm_defaults.get("cpus", 2))
        self.cpu_spin.setRange(1, 16)
        form2.addRow("CPU (núcleos):", self.cpu_spin)
        
        self.ram_spin = QSpinBox()
        self.ram_spin.setValue(vm_defaults.get("ram", 1024))
        self.ram_spin.setRange(256, 16384)
        self.ram_spin.setSuffix(" MB")
        form2.addRow("RAM:", self.ram_spin)
        
        self.vga_combo = QComboBox()
        self.vga_combo.addItems(["qxl", "virtio", "vmware", "vga"])
        self.vga_combo.setCurrentText(vm_defaults.get("vga", "qxl"))
        form2.addRow("Tarjeta Gráfica:", self.vga_combo)
        
        main_layout.addLayout(form2)
        main_layout.addStretch()
        
        widget.setLayout(main_layout)
        return widget
    
    def create_paths_tab(self):
        """Crea la pestaña de directorios"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("<b>Directorios por Defecto</b>")
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        
        # Directorio de ISOs
        iso_layout = QHBoxLayout()
        self.iso_path = QLineEdit()
        self.iso_path.setText(self.config.get_iso_dir())
        self.iso_path.setReadOnly(True)
        iso_layout.addWidget(self.iso_path)
        
        iso_browse = QPushButton("Examinar...")
        iso_browse.clicked.connect(self.browse_iso_dir)
        iso_layout.addWidget(iso_browse)
        
        form_layout.addRow("Directorio de ISOs:", iso_layout)
        
        # Directorio de discos
        disk_layout = QHBoxLayout()
        self.disk_path = QLineEdit()
        self.disk_path.setText(self.config.get_disk_dir())
        self.disk_path.setReadOnly(True)
        disk_layout.addWidget(self.disk_path)
        
        disk_browse = QPushButton("Examinar...")
        disk_browse.clicked.connect(self.browse_disk_dir)
        disk_layout.addWidget(disk_browse)
        
        form_layout.addRow("Directorio de Discos:", disk_layout)
        
        layout.addLayout(form_layout)
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def create_ui_tab(self):
        """Crea la pestaña de interfaz"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        title = QLabel("<b>Interfaz de Usuario</b>")
        layout.addWidget(title)
        
        form_layout = QFormLayout()
        
        self.theme_combo = QComboBox()
        self.theme_combo.addItems(["Claro", "Oscuro"])
        current_theme = self.config.get_theme()
        self.theme_combo.setCurrentText("Claro" if current_theme == "light" else "Oscuro")
        form_layout.addRow("Tema:", self.theme_combo)
        
        layout.addLayout(form_layout)
        layout.addSpacing(20)
        
        info = QLabel(
            "<b>Información:</b><br><br>"
            "<b>Archivo de configuración:</b><br>"
            f"{self.config.CONFIG_FILE}<br><br>"
            "Los cambios se guardan automáticamente."
        )
        info.setWordWrap(True)
        layout.addWidget(info)
        
        layout.addStretch()
        
        widget.setLayout(layout)
        return widget
    
    def browse_iso_dir(self):
        """Abre diálogo para seleccionar directorio de ISOs"""
        path = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar directorio de ISOs",
            self.iso_path.text()
        )
        if path:
            self.iso_path.setText(path)
    
    def browse_disk_dir(self):
        """Abre diálogo para seleccionar directorio de discos"""
        path = QFileDialog.getExistingDirectory(
            self,
            "Seleccionar directorio de discos",
            self.disk_path.text()
        )
        if path:
            self.disk_path.setText(path)
    
    def save_settings(self):
        """Guarda los cambios de configuración"""
        try:
            # Aceleración
            accel_type = self.accel_combo.currentData()
            self.config.set_acceleration_type(accel_type)
            
            # Valores por defecto de VM
            vm_defaults = {
                "cpus": self.cpu_spin.value(),
                "ram": self.ram_spin.value(),
                "vga": self.vga_combo.currentText()
            }
            self.config.set_vm_defaults(vm_defaults)
            
            # Directorios
            self.config.set_iso_dir(self.iso_path.text())
            self.config.set_disk_dir(self.disk_path.text())
            
            # Tema
            theme = "light" if self.theme_combo.currentText() == "Claro" else "dark"
            self.config.set_theme(theme)
            
            QMessageBox.information(self, "Éxito", "Configuración guardada correctamente")
            
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando configuración: {e}")
    
    def reset_defaults(self):
        """Restaura la configuración a valores por defecto"""
        reply = QMessageBox.question(
            self,
            "Confirmar",
            "¿Restaurar todos los valores a su estado por defecto?",
            QMessageBox.Yes | QMessageBox.No
        )
        
        if reply == QMessageBox.Yes:
            try:
                from qemu_adapters.config_manager import ConfigManager
                self.config.save_config(ConfigManager.DEFAULT_CONFIG.copy())
                self.init_ui()
                QMessageBox.information(self, "Éxito", "Configuración restaurada")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error restaurando: {e}")