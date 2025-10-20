"""
Diálogo para configurar video
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QLabel, QComboBox,
    QCheckBox, QSpinBox, QTextEdit, QScrollArea, QWidget, QPushButton, QFormLayout
)


class VideoDialog(QDialog):
    """Diálogo para configurar video"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Configuración de Video")
        self.setGeometry(100, 100, 700, 600)
        
        # Usar QVBoxLayout para poder usar addSpacing()
        main_layout = QVBoxLayout()
        
        # Sección de emulación de video
        layout = QFormLayout()
        layout.addWidget(QLabel("<b>Emulación de Video</b>"))
        
        self.vga_type = QComboBox()
        self.vga_type.addItems(["qxl", "virtio", "vmware", "vga", "cirrus", "std"])
        self.vga_type.currentTextChanged.connect(self.update_video_info)
        layout.addRow("Tipo de Tarjeta Gráfica:", self.vga_type)
        
        main_layout.addLayout(layout)
        main_layout.addSpacing(15)
        
        # Sección de resolución
        layout2 = QFormLayout()
        layout2.addWidget(QLabel("<b>Resolución y Color</b>"))
        
        self.resolution = QComboBox()
        self.resolution.addItems(["1024x768", "1280x1024", "1366x768", "1600x1200", "1920x1080", "2560x1440", "3840x2160"])
        layout2.addRow("Resolución:", self.resolution)
        
        self.color_depth = QComboBox()
        self.color_depth.addItems(["8 bits", "16 bits", "24 bits", "32 bits"])
        self.color_depth.setCurrentText("24 bits")
        layout2.addRow("Profundidad de Color:", self.color_depth)
        
        main_layout.addLayout(layout2)
        main_layout.addSpacing(15)
        
        # Sección de opciones avanzadas
        layout3 = QFormLayout()
        layout3.addWidget(QLabel("<b>Opciones Avanzadas</b>"))
        
        self.vram = QSpinBox()
        self.vram.setValue(64)
        self.vram.setRange(4, 512)
        self.vram.setSuffix(" MB")
        layout3.addRow("Memoria VRAM:", self.vram)
        
        self.gl_acceleration = QCheckBox("Aceleración OpenGL")
        layout3.addRow("Aceleración GL:", self.gl_acceleration)
        
        self.virgl = QCheckBox("Virgl (aceleración 3D)")
        layout3.addRow("Virgl:", self.virgl)
        
        self.monitors = QSpinBox()
        self.monitors.setValue(1)
        self.monitors.setRange(1, 4)
        layout3.addRow("Monitores:", self.monitors)
        
        main_layout.addLayout(layout3)
        main_layout.addSpacing(15)
        
        # Información
        self.video_info = QTextEdit()
        self.video_info.setReadOnly(True)
        self.video_info.setMaximumHeight(150)
        main_layout.addWidget(QLabel("<b>Información:</b>"))
        main_layout.addWidget(self.video_info)
        
        self.update_video_info(self.vga_type.currentText())
        
        # Contenedor con scroll
        widget = QWidget()
        widget.setLayout(main_layout)
        
        scroll = QScrollArea()
        scroll.setWidget(widget)
        scroll.setWidgetResizable(True)
        
        # Layout final
        final_layout = QVBoxLayout()
        final_layout.addWidget(scroll)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        final_layout.addWidget(close_btn)
        
        self.setLayout(final_layout)
    
    def update_video_info(self, vga_type):
        info = f"<b>Tipo de Tarjeta: {vga_type}</b><br><br>"
        
        descriptions = {
            "qxl": "Optimizada para SPICE, excelente rendimiento",
            "virtio": "Recomendada, mejor rendimiento 3D",
            "vmware": "Compatible con VMware",
            "vga": "Estándar VGA compatible",
            "cirrus": "Legada, para SO antiguos",
            "std": "Estándar, compatibilidad máxima"
        }
        
        info += descriptions.get(vga_type, "Información no disponible")
        self.video_info.setHtml(info)