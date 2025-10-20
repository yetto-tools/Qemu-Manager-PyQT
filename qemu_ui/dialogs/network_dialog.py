"""
Diálogo para gestionar redes
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QComboBox, QCheckBox, QFormLayout, QTextEdit, QTabWidget, QWidget,
    QSpinBox, QMessageBox
)

class NetworkDialog(QDialog):
    """Diálogo para gestionar redes"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Administrador de Redes")
        self.setGeometry(100, 100, 800, 500)
        
        layout = QVBoxLayout()
        self.tabs = QTabWidget()
        
        create_tab = self.create_network_tab()
        self.tabs.addTab(create_tab, "Crear Red")
        
        config_tab = self.network_config_tab()
        self.tabs.addTab(config_tab, "Configurar Red")
        
        layout.addWidget(self.tabs)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def create_network_tab(self):
        widget = QWidget()
        layout = QFormLayout()
        
        self.net_name = QLineEdit()
        layout.addRow("Nombre de la Red:", self.net_name)
        
        self.net_type = QComboBox()
        self.net_type.addItems(["user", "bridge", "tap", "vde"])
        self.net_type.currentTextChanged.connect(self.update_network_info)
        layout.addRow("Tipo de Red:", self.net_type)
        
        self.net_subnet = QLineEdit()
        self.net_subnet.setText("192.168.122.0/24")
        layout.addRow("Subred (CIDR):", self.net_subnet)
        
        self.net_dhcp = QCheckBox("Habilitar DHCP")
        self.net_dhcp.setChecked(True)
        layout.addRow("DHCP:", self.net_dhcp)
        
        self.net_ipv6 = QCheckBox("Habilitar IPv6")
        layout.addRow("IPv6:", self.net_ipv6)
        
        self.net_info = QTextEdit()
        self.net_info.setReadOnly(True)
        self.net_info.setMaximumHeight(150)
        layout.addRow("Información:", self.net_info)
        
        btn_create = QPushButton("Crear Red")
        btn_create.clicked.connect(self.create_network)
        layout.addRow("", btn_create)
        
        widget.setLayout(layout)
        return widget
    
    def network_config_tab(self):
        """Crea la pestaña de configuración de red"""
        widget = QWidget()
        # Usar QVBoxLayout en lugar de QFormLayout para poder usar addSpacing()
        main_layout = QVBoxLayout()
        
        # Título
        title = QLabel("<b>Modelo de Interfaz:</b>")
        main_layout.addWidget(title)
        
        # Opciones de modelo
        self.model_virtio = QCheckBox("virtio (recomendado)")
        self.model_virtio.setChecked(True)
        main_layout.addWidget(self.model_virtio)
        
        self.model_e1000 = QCheckBox("e1000 (Intel)")
        main_layout.addWidget(self.model_e1000)
        
        self.model_rtl = QCheckBox("rtl8139 (Realtek)")
        main_layout.addWidget(self.model_rtl)
        
        # Espaciador
        main_layout.addSpacing(20)
        
        # Configuración avanzada
        form_layout = QFormLayout()
        
        self.net_mtu = QSpinBox()
        self.net_mtu.setValue(1500)
        self.net_mtu.setRange(68, 65535)
        form_layout.addRow("MTU (bytes):", self.net_mtu)
        
        self.net_vlan = QSpinBox()
        self.net_vlan.setValue(0)
        self.net_vlan.setRange(0, 4094)
        form_layout.addRow("VLAN ID:", self.net_vlan)
        
        main_layout.addLayout(form_layout)
        main_layout.addStretch()
        
        widget.setLayout(main_layout)
        return widget
    
    def update_network_info(self, net_type):
        """Actualiza la información de la red según el tipo seleccionado"""
        info_text = f"<b>Tipo de Red: {net_type}</b><br><br>"
        
        descriptions = {
            "user": "✓ Sin configuración de red del host<br>✓ NAT automático<br>✓ Fácil de usar",
            "bridge": "✓ VM en la misma red que el host<br>✓ Requiere configuración bridge<br>✓ Mayor control",
            "tap": "✓ Interfaz tap en el host<br>✓ Mayor flexibilidad<br>✓ Requiere permisos root",
            "vde": "✓ Virtual Distributed Ethernet<br>✓ Para entornos complejos<br>✓ Requiere VDE instalado"
        }
        
        info_text += descriptions.get(net_type, "Información no disponible")
        self.net_info.setHtml(info_text)
    
    def create_network(self):
        """Crea una nueva red con la configuración actual"""
        name = self.net_name.text().strip()
        if not name:
            QMessageBox.warning(self, "Error", "Ingrese nombre para la red")
            return
        
        QMessageBox.information(self, "Éxito", f"Red '{name}' configurada")