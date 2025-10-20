# qemu_ui/dialogs/peripherals_dialog.py
"""
Diálogo para administrar periféricos
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QComboBox, QCheckBox, QSpinBox, QListWidget, QFormLayout, QTabWidget, QWidget,QLineEdit
)

class PeripheralsDialog(QDialog):
    """Diálogo para administrar periféricos"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Administrador de Periféricos")
        self.setGeometry(100, 100, 900, 600)
        
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        usb_tab = self.usb_tab()
        self.tabs.addTab(usb_tab, "USB")
        
        audio_tab = self.audio_tab()
        self.tabs.addTab(audio_tab, "Audio")
        
        input_tab = self.input_tab()
        self.tabs.addTab(input_tab, "Entrada (Input)")
        
        serial_tab = self.serial_tab()
        self.tabs.addTab(serial_tab, "Puerto Serial")
        
        other_tab = self.other_tab()
        self.tabs.addTab(other_tab, "Otros")
        
        layout.addWidget(self.tabs)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def usb_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        
        layout.addWidget(QLabel("<b>Controlador USB</b>"))
        
        self.usb_version = QComboBox()
        self.usb_version.addItems(["1.1", "2.0", "3.0", "3.1"])
        self.usb_version.setCurrentText("2.0")
        layout.addRow("Versión USB:", self.usb_version)
        
        self.usb_ports = QSpinBox()
        self.usb_ports.setValue(4)
        self.usb_ports.setRange(1, 16)
        layout.addRow("Puertos USB:", self.usb_ports)
        
        self.usb_redirect = QCheckBox("Habilitar redirección USB")
        layout.addRow("", self.usb_redirect)
        
        widget.setLayout(layout)
        return widget
    
    def audio_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        
        self.audio_enabled = QCheckBox("Habilitar Audio")
        self.audio_enabled.setChecked(True)
        layout.addRow("", self.audio_enabled)
        
        self.audio_driver = QComboBox()
        self.audio_driver.addItems(["pulseaudio", "alsa", "oss", "coreaudio"])
        layout.addRow("Driver de Audio:", self.audio_driver)
        
        self.audio_model = QComboBox()
        self.audio_model.addItems(["ac97", "es1370", "sb16", "hdmi"])
        layout.addRow("Modelo de Audio:", self.audio_model)
        
        widget.setLayout(layout)
        return widget
    
    def input_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        
        self.mouse_type = QComboBox()
        self.mouse_type.addItems(["PS/2", "USB", "Tablet USB"])
        layout.addRow("Tipo de Ratón:", self.mouse_type)
        
        self.keyboard_type = QComboBox()
        self.keyboard_type.addItems(["PS/2", "USB"])
        layout.addRow("Tipo de Teclado:", self.keyboard_type)
        
        self.grab_input = QCheckBox("Captura automática de entrada")
        layout.addRow("", self.grab_input)
        
        widget.setLayout(layout)
        return widget
    
    def serial_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        
        self.serial_enabled = QCheckBox("Habilitar Puerto Serial")
        layout.addRow("", self.serial_enabled)
        
        self.serial_device = QComboBox()
        self.serial_device.addItems(["pty", "file", "socket", "tcp"])
        layout.addRow("Tipo de Dispositivo:", self.serial_device)
        
        self.serial_path = QLineEdit()
        self.serial_path.setText("/tmp/qemu_serial")
        layout.addRow("Ruta/Host:", self.serial_path)
        
        widget.setLayout(layout)
        return widget
    
    def other_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        
        self.parallel = QCheckBox("Habilitar Puerto Paralelo")
        layout.addRow("", self.parallel)
        
        self.watchdog = QCheckBox("Habilitar Watchdog Timer")
        layout.addRow("", self.watchdog)
        
        self.virtio_rng = QCheckBox("Habilitar RNG Virtio")
        layout.addRow("", self.virtio_rng)
        
        self.balloon = QCheckBox("Habilitar Balloon Device")
        self.balloon.setChecked(True)
        layout.addRow("", self.balloon)
        
        widget.setLayout(layout)
        return widget


