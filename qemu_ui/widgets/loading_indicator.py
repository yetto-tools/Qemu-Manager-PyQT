# qemu_ui/widgets/loading_indicator.py
"""
Widget de indicador de carga animado
"""

from PyQt5.QtWidgets import QWidget, QVBoxLayout, QLabel
from PyQt5.QtCore import QTimer, Qt, QSize
from PyQt5.QtGui import QFont, QColor, QPainter, QPen
import math


class LoadingSpinner(QWidget):
    """Spinner animado de carga"""
    
    def __init__(self, parent=None, size=50, speed=100):
        super().__init__(parent)
        self.size = size
        self.angle = 0
        self.speed = speed
        self.timer = QTimer()
        self.timer.timeout.connect(self.rotate)
        
        self.setFixedSize(size, size)
        self.timer.start(self.speed)
    
    def rotate(self):
        """Rota el spinner"""
        self.angle = (self.angle + 6) % 360
        self.update()
    
    def paintEvent(self, event):
        """Dibuja el spinner"""
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        
        # Centro
        center_x = self.width() / 2
        center_y = self.height() / 2
        
        # Dibujar circulos
        painter.translate(center_x, center_y)
        painter.rotate(self.angle)
        
        # Color degradado
        for i in range(12):
            painter.save()
            painter.rotate(i * 30)
            
            # Opacidad decreciente
            opacity = int(255 * (1 - i / 12))
            pen = QPen(QColor(0, 120, 215, opacity))
            pen.setWidth(2)
            pen.setCapStyle(Qt.RoundCap)
            painter.setPen(pen)
            
            # Linea
            painter.drawLine(0, self.size // 4, 0, self.size // 3)
            painter.restore()
    
    def stop(self):
        """Detiene la animacion"""
        self.timer.stop()
    
    def start(self):
        """Inicia la animacion"""
        self.timer.start()


class LoadingDialog(QWidget):
    """Dialogo de carga con spinner y mensaje"""
    
    def __init__(self, parent=None, message="Cargando..."):
        super().__init__(parent)
        self.init_ui(message)
    
    def init_ui(self, message):
        """Inicializa UI"""
        layout = QVBoxLayout()
        layout.setSpacing(20)
        layout.setContentsMargins(40, 40, 40, 40)
        
        # Spinner
        self.spinner = LoadingSpinner(self, size=60, speed=50)
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Mensaje
        self.message_label = QLabel(message)
        msg_font = QFont()
        msg_font.setPointSize(11)
        self.message_label.setFont(msg_font)
        self.message_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(self.message_label)
        
        # Progreso
        self.progress_label = QLabel("")
        prog_font = QFont()
        prog_font.setPointSize(9)
        self.progress_label.setFont(prog_font)
        self.progress_label.setAlignment(Qt.AlignCenter)
        self.progress_label.setStyleSheet("color: gray;")
        layout.addWidget(self.progress_label)
        
        self.setLayout(layout)
        self.setStyleSheet("""
            LoadingDialog {
                background-color: white;
                border-radius: 10px;
                border: 1px solid #e0e0e0;
            }
        """)
    
    def update_message(self, message):
        """Actualiza el mensaje"""
        self.message_label.setText(message)
    
    def update_progress(self, progress):
        """Actualiza el progreso"""
        self.progress_label.setText(progress)
    
    def stop(self):
        """Detiene el spinner"""
        self.spinner.stop()


class LoadingOverlay(QWidget):
    """Overlay de carga semi-transparente"""
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.init_ui()
    
    def init_ui(self):
        """Inicializa UI"""
        self.setStyleSheet("""
            LoadingOverlay {
                background-color: rgba(255, 255, 255, 230);
            }
        """)
        
        layout = QVBoxLayout()
        layout.setAlignment(Qt.AlignCenter)
        
        # Spinner grande
        self.spinner = LoadingSpinner(self, size=80, speed=50)
        layout.addWidget(self.spinner, alignment=Qt.AlignCenter)
        
        # Mensaje
        self.message = QLabel("Por favor espera...")
        msg_font = QFont()
        msg_font.setPointSize(12)
        msg_font.setBold(True)
        self.message.setFont(msg_font)
        self.message.setAlignment(Qt.AlignCenter)
        layout.addSpacing(20)
        layout.addWidget(self.message)
        
        # Detalles
        self.details = QLabel("")
        det_font = QFont()
        det_font.setPointSize(10)
        self.details.setFont(det_font)
        self.details.setAlignment(Qt.AlignCenter)
        self.details.setStyleSheet("color: #666;")
        layout.addWidget(self.details)
        
        self.setLayout(layout)
    
    def update_message(self, message, details=""):
        """Actualiza mensaje y detalles"""
        self.message.setText(message)
        self.details.setText(details)
    
    def stop(self):
        """Detiene la animacion"""
        self.spinner.stop()