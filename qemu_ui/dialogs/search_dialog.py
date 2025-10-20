# qemu_ui/dialogs/search_dialog.py
"""
Diálogo para buscar discos y máquinas
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QListWidget, QCheckBox, QFileDialog, QMessageBox
)
from pathlib import Path
import os


class SearchDialog(QDialog):
    """Diálogo para buscar discos y máquinas"""
    
    def __init__(self, parent=None, storage_adapter=None):
        super().__init__(parent)
        self.storage = storage_adapter
        self.init_ui()
    
    def init_ui(self):
        self.setWindowTitle("Buscar Máquinas y Discos")
        self.setGeometry(150, 150, 700, 500)
        
        layout = QVBoxLayout()
        
        search_layout = QHBoxLayout()
        search_layout.addWidget(QLabel("Ruta de búsqueda:"))
        
        self.search_path = QLineEdit()
        from pathlib import Path
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
        
        layout.addLayout(options_layout)
        
        search_btn = QPushButton("🔍 Iniciar búsqueda")
        search_btn.clicked.connect(self.start_search)
        layout.addWidget(search_btn)
        
        self.results_list = QListWidget()
        layout.addWidget(self.results_list)
        
        close_btn = QPushButton("Cerrar")
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        self.setLayout(layout)
    
    def browse_search_path(self):
        path = QFileDialog.getExistingDirectory(self, "Seleccionar directorio")
        if path:
            self.search_path.setText(path)
    
    def start_search(self):
        from pathlib import Path
        self.results_list.clear()
        
        search_path = self.search_path.text()
        if not os.path.exists(search_path):
            QMessageBox.warning(self, "Error", "La ruta no existe")
            return
        
        extensions = []
        if self.search_qcow2.isChecked():
            extensions.append("*.qcow2")
        if self.search_iso.isChecked():
            extensions.append("*.iso")
        
        try:
            found = 0
            for ext in extensions:
                for file_path in Path(search_path).rglob(ext):
                    if file_path.is_file():
                        self.results_list.addItem(str(file_path))
                        found += 1
            
            QMessageBox.information(self, "Búsqueda", f"Se encontraron {found} archivo(s)")
        except Exception as e:
            QMessageBox.critical(self, "Error", str(e))


        
        title = QLabel("QEMU Manager Pro")
        title_font = QFont()
        title_font.setPointSize(18)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        version = QLabel("Versión 3.0 - Arquitectura Hexagonal")
        version_font = QFont()
        version_font.setPointSize(11)
        version.setFont(version_font)
        layout.addWidget(version)
        
        layout.addSpacing(20)
        
        description = QLabel(
            "Gestor gráfico completo para máquinas virtuales QEMU con arquitectura hexagonal.\n\n"
            "<b>Características:</b><br>"
            "• Crear y gestionar máquinas virtuales<br>"
            "• Detección automática de VMs existentes<br>"
            "• Administrador completo de discos virtuales<br>"
            "• Configuración avanzada de hardware, video y red<br>"
            "• Administrador de periféricos (USB, Audio, Serial)<br>"
            "• Búsqueda de discos y máquinas<br>"
            "• Importación y exportación de configuraciones<br><br>"
            "<b>Requisitos:</b><br>"
            "• QEMU instalado en el sistema<br>"
            "• PyQt5<br>"
            "• Permisos de usuario para QEMU"
        )
        layout.addWidget(description)
        
        layout.addSpacing(20)
        
        copyright_label = QLabel("© 2025 QEMU Manager\nLicencia: GPL v3\nArquitectura: Hexagonal (Puertos y Adaptadores)")
        copyright_label.setStyleSheet("color: gray; font-size: 9pt;")
        layout.addWidget(copyright_label)
        
        layout.addStretch()
        
        ok_btn = QPushButton("Cerrar")
        ok_btn.clicked.connect(self.close)
        layout.addWidget(ok_btn)
        
        self.setLayout(layout)


