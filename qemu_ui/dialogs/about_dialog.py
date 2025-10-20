# qemu_ui/dialogs/about_dialog.py
"""
Diálogo de información sobre la aplicación QEMU Manager

UBICACIÓN: qemu_ui/dialogs/about_dialog.py
PROPÓSITO: Mostrar información de la aplicación
"""

from PyQt5.QtWidgets import (
    QDialog, QVBoxLayout, QPushButton, QLabel, QTextEdit, QTabWidget, QWidget
)
from PyQt5.QtGui import QFont, QPixmap
from PyQt5.QtCore import Qt
import config


class AboutDialog(QDialog):
    """
    Diálogo que muestra información sobre QEMU Manager
    
    Características:
    - Información de la aplicación
    - Características principales
    - Requisitos del sistema
    - Información de licencia
    - Créditos
    """
    
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Acerca de QEMU Manager")
        self.setGeometry(200, 200, 700, 600)
        self.setMinimumWidth(700)
        self.setMinimumHeight(600)
        
        self.init_ui()
    
    def init_ui(self):
        """Inicializa la interfaz del diálogo"""
        
        main_layout = QVBoxLayout()
        main_layout.setSpacing(15)
        main_layout.setContentsMargins(20, 20, 20, 20)
        
        # ==================== SECCIÓN DE TÍTULO ====================
        title_layout = self.create_title_section()
        main_layout.addLayout(title_layout)
        
        # ==================== SEPARADOR ====================
        separator = QLabel("-" * 50)
        main_layout.addWidget(separator)
        
        # ==================== PESTAÑAS ====================
        self.tabs = QTabWidget()
        
        # Pestaña Información
        info_tab = self.create_info_tab()
        self.tabs.addTab(info_tab, "📋 Información")
        
        # Pestaña Características
        features_tab = self.create_features_tab()
        self.tabs.addTab(features_tab, "✨ Características")
        
        # Pestaña Requisitos
        requirements_tab = self.create_requirements_tab()
        self.tabs.addTab(requirements_tab, "⚙️ Requisitos")
        
        # Pestaña Licencia
        license_tab = self.create_license_tab()
        self.tabs.addTab(license_tab, "📜 Licencia")
        
        # Pestaña Créditos
        credits_tab = self.create_credits_tab()
        self.tabs.addTab(credits_tab, "👥 Créditos")
        
        main_layout.addWidget(self.tabs)
        
        # ==================== BOTONES ====================
        button_layout = self.create_button_section()
        main_layout.addLayout(button_layout)
        
        self.setLayout(main_layout)
    
    def create_title_section(self):
        """Crea la sección de título con información general"""
        from PyQt5.QtWidgets import QHBoxLayout
        
        layout = QHBoxLayout()
        
        # Título principal
        title = QLabel("QEMU Manager Pro")
        title_font = QFont()
        title_font.setPointSize(20)
        title_font.setBold(True)
        title.setFont(title_font)
        layout.addWidget(title)
        
        layout.addStretch()
        
        # Versión
        version_widget = QWidget()
        version_layout = QVBoxLayout()
        
        version_label = QLabel(f"Versión {config.APP_VERSION}")
        version_font = QFont()
        version_font.setPointSize(12)
        version_font.setBold(True)
        version_label.setFont(version_font)
        version_layout.addWidget(version_label)
        
        subtitle = QLabel("Gestor de Máquinas Virtuales QEMU")
        subtitle_font = QFont()
        subtitle_font.setPointSize(10)
        subtitle_font.setItalic(True)
        subtitle.setFont(subtitle_font)
        subtitle.setStyleSheet("color: gray;")
        version_layout.addWidget(subtitle)
        
        version_widget.setLayout(version_layout)
        layout.addWidget(version_widget)
        
        return layout
    
    def create_info_tab(self):
        """Crea la pestaña de información general"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        info_text = f"""
        <h3>QEMU Manager Pro</h3>
        
        <p><b>Versión:</b> {config.APP_VERSION}</p>
        <p><b>Autor:</b> {config.APP_AUTHOR}</p>
        <p><b>Descripción:</b> {config.APP_DESCRIPTION}</p>
        
        <h4>Acerca de:</h4>
        <p>QEMU Manager es una aplicación gráfica completa para gestionar máquinas virtuales 
        QEMU en Linux, macOS y WSL. Proporciona una interfaz intuitiva para crear, configurar, 
        iniciar y detener máquinas virtuales sin necesidad de usar la línea de comandos.</p>
        
        <p>La aplicación implementa <b>Arquitectura Hexagonal (Puertos y Adaptadores)</b>, 
        lo que garantiza:</p>
        <ul>
            <li>Código limpio y mantenible</li>
            <li>Fácil de probar (testeable)</li>
            <li>Independencia de frameworks</li>
            <li>Reutilizable en múltiples interfaces</li>
        </ul>
        
        <h4>Características Principales:</h4>
        <ul>
            <li>✓ Crear y gestionar máquinas virtuales</li>
            <li>✓ Detección automática de VMs existentes</li>
            <li>✓ Administrador completo de discos virtuales</li>
            <li>✓ Crear y convertir formatos de disco</li>
            <li>✓ Configuración avanzada de hardware</li>
            <li>✓ Administrador de redes</li>
            <li>✓ Configuración de video</li>
            <li>✓ Administrador de periféricos</li>
            <li>✓ Búsqueda de discos e imágenes ISO</li>
            <li>✓ Importación y exportación de configuraciones</li>
        </ul>
        """
        
        text_edit = QTextEdit()
        text_edit.setHtml(info_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        widget.setLayout(layout)
        return widget
    
    def create_features_tab(self):
        """Crea la pestaña de características"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        features_text = """
        <h3>Características de QEMU Manager</h3>
        
        <h4>🖥️ Gestión de Máquinas Virtuales</h4>
        <ul>
            <li>Crear nuevas máquinas virtuales</li>
            <li>Configurar CPU, RAM, disco y otros parámetros</li>
            <li>Iniciar, pausar y detener VMs</li>
            <li>Eliminar VMs existentes</li>
            <li>Detección automática de VMs en el sistema</li>
        </ul>
        
        <h4>💾 Administrador de Discos</h4>
        <ul>
            <li>Crear nuevos discos virtuales</li>
            <li>Soporta múltiples formatos: QCOW2, RAW, VDI, VMDK</li>
            <li>Convertir entre formatos</li>
            <li>Gestionar discos existentes</li>
            <li>Preconfiguración de tamaños estándar</li>
        </ul>
        
        <h4>🌐 Configuración de Red</h4>
        <ul>
            <li>Tipos de red: user, bridge, tap, vde</li>
            <li>Configuración de interfaces</li>
            <li>Soporte para DHCP e IPv6</li>
            <li>VLAN y MTU personalizados</li>
        </ul>
        
        <h4>🎬 Configuración de Video</h4>
        <ul>
            <li>Tipos de tarjetas gráficas: QXL, Virtio, VMware, VGA</li>
            <li>Múltiples resoluciones disponibles</li>
            <li>Configuración de profundidad de color</li>
            <li>Aceleración OpenGL y Virgl</li>
            <li>Soporte para múltiples monitores</li>
        </ul>
        
        <h4>🔌 Administrador de Periféricos</h4>
        <ul>
            <li>Configuración de puertos USB</li>
            <li>Configuración de audio</li>
            <li>Dispositivos de entrada (ratón, teclado)</li>
            <li>Puertos seriales</li>
            <li>Otros periféricos (paralelo, watchdog, etc)</li>
        </ul>
        
        <h4>🔍 Búsqueda y Descubrimiento</h4>
        <ul>
            <li>Buscar discos en el sistema de archivos</li>
            <li>Escanear directorios recursivamente</li>
            <li>Importar VMs existentes</li>
            <li>Filtrar por tipo de archivo</li>
        </ul>
        """
        
        text_edit = QTextEdit()
        text_edit.setHtml(features_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        widget.setLayout(layout)
        return widget
    
    def create_requirements_tab(self):
        """Crea la pestaña de requisitos del sistema"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        requirements_text = f"""
        <h3>Requisitos del Sistema</h3>
        
        <h4>Requisitos Mínimos:</h4>
        <ul>
            <li><b>Python:</b> 3.8 o superior</li>
            <li><b>QEMU:</b> 4.2 o superior</li>
            <li><b>RAM:</b> 2 GB mínimo</li>
            <li><b>Espacio en disco:</b> 500 MB para la aplicación</li>
            <li><b>SO:</b> Linux, macOS o WSL (Windows Subsystem for Linux)</li>
        </ul>
        
        <h4>Requisitos Recomendados:</h4>
        <ul>
            <li><b>Python:</b> 3.10 o superior</li>
            <li><b>QEMU:</b> 6.0 o superior</li>
            <li><b>RAM:</b> 4 GB o más</li>
            <li><b>Procesador:</b> Intel VT-x o AMD-V (para KVM)</li>
            <li><b>SO:</b> Linux de 64 bits</li>
        </ul>
        
        <h4>Dependencias Python:</h4>
        <ul>
            <li><b>PyQt5:</b> 5.15+</li>
            <li><b>psutil:</b> Para monitoreo del sistema</li>
        </ul>
        
        <h4>Dependencias del Sistema:</h4>
        <ul>
            <li><b>qemu-system-x86_64:</b> Para máquinas de 64 bits</li>
            <li><b>qemu-img:</b> Para gestión de imágenes de disco</li>
            <li><b>KVM (opcional):</b> Para aceleración por hardware</li>
        </ul>
        
        <h4>Instalación de Dependencias:</h4>
        <p><b>En Ubuntu/Debian:</b></p>
        <pre>sudo apt update
sudo apt install qemu-system-x86 qemu-utils python3-pyqt5
pip install psutil</pre>
        
        <p><b>En Fedora/RHEL:</b></p>
        <pre>sudo dnf install qemu-system-x86 qemu-img python3-pyqt5
pip install psutil</pre>
        
        <p><b>En macOS:</b></p>
        <pre>brew install qemu pyqt5
pip install psutil</pre>
        """
        
        text_edit = QTextEdit()
        text_edit.setHtml(requirements_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        widget.setLayout(layout)
        return widget
    
    def create_license_tab(self):
        """Crea la pestaña de licencia"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        license_text = """
        <h3>Licencia GPL v3</h3>
        
        <p>QEMU Manager está licenciado bajo la GNU General Public License v3.0</p>
        
        <h4>Derechos de Uso:</h4>
        <ul>
            <li><b>✓ Libertad:</b> Usar el software con cualquier propósito</li>
            <li><b>✓ Estudio:</b> Examinar y estudiar el código fuente</li>
            <li><b>✓ Modificación:</b> Modificar el código para tus necesidades</li>
            <li><b>✓ Distribución:</b> Compartir mejoras con la comunidad</li>
        </ul>
        
        <h4>Obligaciones:</h4>
        <ul>
            <li><b>⚠️ Atribución:</b> Reconocer a los autores originales</li>
            <li><b>⚠️ Copyleft:</b> Las modificaciones deben mantenerse bajo GPL</li>
            <li><b>⚠️ Licencia:</b> Incluir copia de la licencia</li>
            <li><b>⚠️ Cambios:</b> Documentar los cambios realizados</li>
        </ul>
        
        <h4>Descargo de Responsabilidad:</h4>
        <p>Este software se proporciona "TAL COMO ESTÁ", sin garantía de ningún tipo, 
        explícita o implícita, incluyendo pero no limitado a garantías de comerciabilidad, 
        aptitud para un propósito particular y no infracción.</p>
        
        <p>Los autores no serán responsables de ningún daño directo, indirecto, incidental, 
        especial, ejemplar o consecuente (incluyendo pero no limitado a, la adquisición de 
        bienes o servicios sustitutos; pérdida de uso, datos o ganancias; o interrupción del 
        negocio) causado por cualquier teoría de responsabilidad, ya sea por contrato, 
        responsabilidad objetiva o agravio (incluyendo negligencia o de otro modo).</p>
        
        <h4>Licencia Completa:</h4>
        <p>Para leer la licencia completa, visite: 
        <a href="https://www.gnu.org/licenses/gpl-3.0.html">https://www.gnu.org/licenses/gpl-3.0.html</a></p>
        """
        
        text_edit = QTextEdit()
        text_edit.setHtml(license_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        widget.setLayout(layout)
        return widget
    
    def create_credits_tab(self):
        """Crea la pestaña de créditos"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        credits_text = """
        <h3>Créditos</h3>
        
        <h4>Desarrollo:</h4>
        <ul>
            <li><b>QEMU Manager Team</b> - Desarrollo principal</li>
            <li>Arquitectura Hexagonal implementada</li>
            <li>Interfaz PyQt5</li>
        </ul>
        
        <h4>Tecnologías Utilizadas:</h4>
        <ul>
            <li><b>QEMU:</b> Emulador y virtualizador (https://www.qemu.org)</li>
            <li><b>PyQt5:</b> Framework GUI para Python (https://www.riverbankcomputing.com/software/pyqt)</li>
            <li><b>Python:</b> Lenguaje de programación (https://www.python.org)</li>
            <li><b>psutil:</b> Librería para monitoreo del sistema</li>
        </ul>
        
        <h4>Patrones y Arquitectura:</h4>
        <ul>
            <li><b>Arquitectura Hexagonal:</b> Puertos y Adaptadores</li>
            <li><b>Patrón Repository:</b> Para abstracción de datos</li>
            <li><b>Patrón UseCase:</b> Para lógica de negocio</li>
            <li><b>Patrón Presenter:</b> Para separación de presentación</li>
            <li><b>Inyección de Dependencias:</b> Para desacoplamiento</li>
            <li><b>Observer Pattern:</b> Para notificaciones</li>
        </ul>
        
        <h4>Herramientas de Desarrollo:</h4>
        <ul>
            <li><b>Git:</b> Control de versiones</li>
            <li><b>GitHub:</b> Repositorio del código</li>
            <li><b>pytest:</b> Framework de testing</li>
        </ul>
        
        <h4>Comunidad:</h4>
        <p>Agradecemos a la comunidad de QEMU y Python por sus valiosas 
        contribuciones, reportes de bugs y sugerencias de mejora.</p>
        
        <h4>Contribuciones:</h4>
        <p>¿Quieres contribuir? Puedes:</p>
        <ul>
            <li>Reportar bugs en GitHub Issues</li>
            <li>Sugerir nuevas características</li>
            <li>Enviar pull requests con mejoras</li>
            <li>Ayudar con la documentación</li>
            <li>Traducir a otros idiomas</li>
        </ul>
        
        <h4>Contacto y Recursos:</h4>
        <ul>
            <li><b>Repositorio:</b> https://github.com/usuario/qemu-manager</li>
            <li><b>Documentación:</b> Wiki del proyecto</li>
            <li><b>Issues:</b> GitHub Issues</li>
            <li><b>Discusiones:</b> GitHub Discussions</li>
        </ul>
        
        <p style="margin-top: 30px; color: gray; font-size: 10pt;">
        Hecho con ❤️ para la comunidad de virtualización
        </p>
        """
        
        text_edit = QTextEdit()
        text_edit.setHtml(credits_text)
        text_edit.setReadOnly(True)
        layout.addWidget(text_edit)
        
        widget.setLayout(layout)
        return widget
    
    def create_button_section(self):
        """Crea la sección de botones"""
        from PyQt5.QtWidgets import QHBoxLayout
        
        layout = QHBoxLayout()
        layout.addStretch()
        
        # Botón Cerrar
        close_btn = QPushButton("Cerrar")
        close_btn.setFixedWidth(100)
        close_btn.clicked.connect(self.close)
        layout.addWidget(close_btn)
        
        return layout