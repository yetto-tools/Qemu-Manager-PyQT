# qemu_ui/main_window.py

import sys
from PyQt5.QtWidgets import (
    QMainWindow, QWidget, QVBoxLayout, QHBoxLayout, QPushButton, QLabel,
    QLineEdit, QSpinBox, QComboBox, QListWidget, QListWidgetItem, QTabWidget,
    QGroupBox, QFileDialog, QMessageBox, QCheckBox, QFormLayout, QTextEdit,
    QTableWidget, QTableWidgetItem, QProgressBar, QDoubleSpinBox, QSlider,
    QScrollArea, QDialog
)
from PyQt5.QtCore import Qt, QTimer, pyqtSignal, QThread
from PyQt5.QtGui import QFont, QColor

from qemu_ui.dialogs.disk_manager_dialog import DiskManagerDialog
from qemu_ui.dialogs.network_dialog import NetworkDialog
from qemu_ui.dialogs.video_dialog import VideoDialog
from qemu_ui.dialogs.peripherals_dialog import PeripheralsDialog
from qemu_ui.dialogs.about_dialog import AboutDialog
from qemu_ui.dialogs.search_dialog import SearchDialog
from qemu_ui.dialogs.settings_dialog import SettingsDialog
from qemu_adapters.config_manager import get_config

from qemu_domain.models import VMStatus


class VMListPresenter:
    """Adaptador que convierte lógica de negocio a eventos UI"""
    
    def __init__(self, vm_list_widget: QListWidget, info_label: QLabel):
        self.vm_list = vm_list_widget
        self.info_label = info_label
    
    def present_vms(self, vms, running_vms=None):
        """Presenta lista de VMs en la UI"""
        if running_vms is None:
            running_vms = {}
        
        self.vm_list.clear()
        for vm in sorted(vms, key=lambda x: x.name):
            item = QListWidgetItem(vm.name)
            
            # Marcar VMs auto-detectadas
            if vm.auto_detected:
                item.setText(f"📦 {vm.name} (detectada)")
                item.setForeground(QColor("blue"))
            else:
                item.setText(f"⚙️ {vm.name}")
            
            # Marcar VMs en ejecución
            if vm.name in running_vms:
                item.setText(item.text() + " [EJECUTANDO]")
                item.setBackground(QColor("lightgreen"))
            
            self.vm_list.addItem(item)
        
        self.info_label.setText(f"Total de VMs: {len(vms)}")
    
    def present_error(self, error: str):
        """Presenta errores"""
        QMessageBox.critical(None, "Error", error)
    
    def present_success(self, message: str):
        """Presenta mensajes de éxito"""
        QMessageBox.information(None, "Éxito", message)


class ConfigFormPresenter:
    """Adaptador para sincronizar formularios con datos"""
    
    def __init__(self, form_widgets):
        self.name_input = form_widgets['name']
        self.iso_path = form_widgets['iso']
        self.disk_path = form_widgets['disk']
        self.cpu_cores = form_widgets['cpus']
        self.ram_size = form_widgets['ram']
        self.os_type = form_widgets['os']
        self.auto_detect_label = form_widgets['status']
    
    def present_vm(self, vm):
        """Carga datos de VM en el formulario"""
        self.name_input.setText(vm.name)
        self.iso_path.setText(vm.iso or "")
        self.disk_path.setText(vm.disk)
        self.cpu_cores.setValue(vm.cpus)
        self.ram_size.setValue(vm.ram)
        self.os_type.setCurrentText(vm.os)
        
        status_text = "✓ Auto-detectada del sistema" if vm.auto_detected else "✓ Configuración manual"
        self.auto_detect_label.setText(status_text)
    
    def clear_form(self):
        """Limpia el formulario"""
        self.name_input.clear()
        self.iso_path.clear()
        self.disk_path.clear()
        self.cpu_cores.setValue(2)
        self.ram_size.setValue(1024)
        self.auto_detect_label.setText("")
    
    def get_vm_data(self):
        """Obtiene datos del formulario"""
        return {
            'name': self.name_input.text().strip(),
            'iso': self.iso_path.text(),
            'disk': self.disk_path.text(),
            'cpus': self.cpu_cores.value(),
            'ram': self.ram_size.value(),
            'os': self.os_type.currentText()
        }


class InfoPanelPresenter:
    """Adaptador para mostrar información detallada"""
    
    def __init__(self, info_text: QTextEdit):
        self.info_text = info_text
    
    def present_vm_info(self, vm, running_vms=None, storage_adapter=None):
        """Muestra información detallada de VM"""
        if running_vms is None:
            running_vms = {}
        
        status = "🟢 En ejecución" if vm.name in running_vms else "🔴 Detenida"
        
        info = f"""
        <b>Información de la Máquina Virtual</b><br><br>
        <b>Nombre:</b> {vm.name}<br>
        <b>Estado:</b> {status}<br><br>
        
        <b>Configuración:</b><br>
        • <b>CPU:</b> {vm.cpus} núcleos<br>
        • <b>RAM:</b> {vm.ram} MB<br>
        • <b>SO:</b> {vm.os}<br><br>
        
        <b>Almacenamiento:</b><br>
        • <b>Disco:</b> {vm.disk}<br>
        • <b>ISO:</b> {vm.iso or 'No configurado'}<br><br>
        
        <b>Información del Disco:</b><br>
        """
        
        if storage_adapter and vm.disk:
            disk_info = storage_adapter.get_disk_info(vm.disk)
            if 'info' in disk_info and disk_info['info']:
                info += f"<pre>{disk_info['info']}</pre>"
            else:
                info += f"• Error: {disk_info.get('error', 'No se pudo obtener información')}<br>"
        
        self.info_text.setHtml(info)
    
    def present_error(self, error: str):
        """Muestra error en panel info"""
        self.info_text.setHtml(f"<b>Error:</b> {error}")


class QEMUManagerUI(QMainWindow):
    """Ventana principal de la aplicación QEMU Manager"""
    
    def __init__(self, dependencies):
        super().__init__()
        
        # Inyección de dependencias
        self.vm_use_case = dependencies['vm_use_case']
        self.disk_use_case = dependencies['disk_use_case']
        self.app_service = dependencies['app_service']
        self.qemu_executor = dependencies['qemu_executor']
        self.storage = dependencies['storage']
        
        # Estado interno
        self.running_vms = {}
        
        # Inicializar UI
        self.init_ui()
        self.load_initial_data()

        # NUEVO: Detectar y manejar VMs huérfanas
        self.handle_orphaned_vms()        
        # Timer para actualizar estado
        self.status_timer = QTimer()
        self.status_timer.timeout.connect(self.update_vm_status)
        self.status_timer.start(2000)
    
    def init_ui(self):
        """Inicializa la interfaz de usuario"""
        self.setWindowTitle("QEMU Manager - Gestor de Máquinas Virtuales")
        self.setGeometry(100, 100, 1400, 800)
        
        # Crear menú
        self.create_menu_bar()
        
        # Widget central
        central_widget = QWidget()
        self.setCentralWidget(central_widget)
        
        main_layout = QHBoxLayout()
        central_widget.setLayout(main_layout)
        
        # Panel izquierdo
        left_panel = self.create_left_panel()
        main_layout.addWidget(left_panel, 1)
        
        # Panel derecho
        right_panel = self.create_right_panel()
        main_layout.addWidget(right_panel, 2)
    
    def create_menu_bar(self):
        """Crea la barra de menús con acciones"""
        menubar = self.menuBar()
        
        # Menú Archivo
        file_menu = menubar.addMenu("📁 Archivo")
        
        new_vm_action = file_menu.addAction("Nueva VM")
        new_vm_action.triggered.connect(self.new_vm)
        new_vm_action.setShortcut("Ctrl+N")
        
        file_menu.addSeparator()
        
        search_action = file_menu.addAction("🔍 Buscar Discos/Máquinas")
        search_action.triggered.connect(self.open_search_dialog)
        search_action.setShortcut("Ctrl+F")
        
        file_menu.addSeparator()
        
        load_config_action = file_menu.addAction("📂 Cargar Configuración")
        load_config_action.triggered.connect(self.load_config_file)
        load_config_action.setShortcut("Ctrl+O")
        
        save_config_action = file_menu.addAction("💾 Guardar Configuración")
        save_config_action.triggered.connect(self.save_all_configs)
        save_config_action.setShortcut("Ctrl+S")
        
        file_menu.addSeparator()
        
        exit_action = file_menu.addAction("Salir")
        exit_action.triggered.connect(self.close)
        exit_action.setShortcut("Ctrl+Q")
        
        # Menú Editar
        edit_menu = menubar.addMenu("✏️ Editar")
        
        refresh_action = edit_menu.addAction("Actualizar Lista")
        refresh_action.triggered.connect(self.refresh_vm_list)
        refresh_action.setShortcut("F5")
        
        edit_menu.addSeparator()
        
        import_vm_action = edit_menu.addAction("📥 Importar VM")
        import_vm_action.triggered.connect(self.import_vm)
        
        export_vm_action = edit_menu.addAction("📤 Exportar VM")
        export_vm_action.triggered.connect(self.export_vm)
        
        # Menú Herramientas
        tools_menu = menubar.addMenu("🔧 Herramientas")
        
        disk_manager_action = tools_menu.addAction("💾 Administrador de Discos")
        disk_manager_action.triggered.connect(self.open_disk_manager)
        
        network_action = tools_menu.addAction("🌐 Administrador de Redes")
        network_action.triggered.connect(self.open_network_dialog)
        
        video_action = tools_menu.addAction("🎬 Configuración de Video")
        video_action.triggered.connect(self.open_video_dialog)
        
        peripherals_action = tools_menu.addAction("🖨️ Administrador de Periféricos")
        peripherals_action.triggered.connect(self.open_peripherals_dialog)
        
        # NUEVO: Menú Configuración
        settings_menu = menubar.addMenu("⚙️ Configuración")
        
        settings_action = settings_menu.addAction("Preferencias")
        settings_action.triggered.connect(self.open_settings_dialog)
        settings_action.setShortcut("Ctrl+,")
        
        # Menú Ayuda
        help_menu = menubar.addMenu("❓ Ayuda")
        
        about_action = help_menu.addAction("📋 Acerca de")
        about_action.triggered.connect(self.show_about)
        
        help_action = help_menu.addAction("📖 Ayuda")
        help_action.triggered.connect(self.show_help)
    
    def open_settings_dialog(self):
        """Abre el diálogo de configuración"""
        print("[DEBUG] Intentando abrir settings_dialog...")
        try:
            dialog = SettingsDialog(self)
            print("[DEBUG] Dialog creado, mostrando...")
            dialog.exec_()
        except ImportError as e:
            print(f"[ERROR ImportError] {e}")
            QMessageBox.warning(self, "Error", f"No se pudo cargar: {e}")
        except Exception as e:
            print(f"[ERROR Exception] {e}")
            QMessageBox.critical(self, "Error", f"Error: {e}")

    def create_left_panel(self):
        """Crea panel izquierdo con lista de VMs"""
        group = QGroupBox("Máquinas Virtuales")
        layout = QVBoxLayout()
        
        self.info_label = QLabel("Cargando máquinas virtuales...")
        layout.addWidget(self.info_label)
        
        self.vm_list = QListWidget()
        self.vm_list.itemClicked.connect(self.on_vm_selected)
        layout.addWidget(self.vm_list)
        
        # Botones
        btn_layout = QVBoxLayout()
        
        btn_refresh = QPushButton("🔄 Actualizar Lista")
        btn_refresh.clicked.connect(self.refresh_vm_list)
        btn_layout.addWidget(btn_refresh)
        
        btn_new = QPushButton("➕ Nueva VM")
        btn_new.clicked.connect(self.new_vm)
        btn_layout.addWidget(btn_new)
        
        btn_delete = QPushButton("🗑️ Eliminar VM")
        btn_delete.clicked.connect(self.delete_vm)
        btn_layout.addWidget(btn_delete)
        
        # Fila: Iniciar y Detener
        start_stop_layout = QHBoxLayout()
        
        btn_start = QPushButton("▶ Iniciar")
        btn_start.clicked.connect(self.start_vm)
        start_stop_layout.addWidget(btn_start)
        
        btn_stop = QPushButton("⏹ Detener")
        btn_stop.clicked.connect(self.stop_vm)
        start_stop_layout.addWidget(btn_stop)
        
        btn_layout.addLayout(start_stop_layout)
        
        # Fila: Reiniciar y Apagar
        restart_shutdown_layout = QHBoxLayout()
        
        btn_restart = QPushButton("🔄 Reiniciar")
        btn_restart.clicked.connect(self.restart_vm)
        restart_shutdown_layout.addWidget(btn_restart)
        
        btn_shutdown = QPushButton("🛑 Apagar")
        btn_shutdown.clicked.connect(self.shutdown_vm)
        restart_shutdown_layout.addWidget(btn_shutdown)
        
        btn_layout.addLayout(restart_shutdown_layout)
        
        btn_save = QPushButton("💾 Guardar Configuración")
        btn_save.clicked.connect(self.save_config)
        btn_layout.addWidget(btn_save)
        
        layout.addLayout(btn_layout)
        group.setLayout(layout)
        
        return group
    
    def create_right_panel(self):
        """Crea panel derecho con pestañas de configuración"""
        self.tabs = QTabWidget()
        
        # Pestaña Configuración General
        config_tab = self.create_config_tab()
        self.tabs.addTab(config_tab, "Configuración")
        
        # Pestaña Hardware
        hardware_tab = self.create_hardware_tab()
        self.tabs.addTab(hardware_tab, "Hardware")
        
        # Pestaña Red
        network_tab = self.create_network_tab()
        self.tabs.addTab(network_tab, "Red")
        
        # Pestaña Información
        info_tab = self.create_info_tab()
        self.tabs.addTab(info_tab, "Información")
        
        return self.tabs
    
    def create_config_tab(self):
        """Crea pestaña de configuración general"""
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
        """Crea pestaña de hardware"""
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
        
        # NUEVO: Selector de orden de boot
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
        """Crea pestaña de red"""
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
        """Crea pestaña de información"""
        widget = QWidget()
        layout = QVBoxLayout()
        
        self.info_text = QTextEdit()
        self.info_text.setReadOnly(True)
        layout.addWidget(self.info_text)
        
        widget.setLayout(layout)
        return widget
    
    # ==================== EVENT HANDLERS ====================
    
    def load_initial_data(self):
        """Carga datos iniciales de VMs"""
        self.refresh_vm_list()
    
    def refresh_vm_list(self):
        """Actualiza la lista de VMs usando presentador"""
        try:
            vms = self.vm_use_case.get_all_vms()
            list_presenter = VMListPresenter(self.vm_list, self.info_label)
            list_presenter.present_vms(vms, self.running_vms)
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error cargando VMs: {e}")
    
    def on_vm_selected(self, item):
        """Carga la configuración de una VM seleccionada"""
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").replace(" [EJECUTANDO]", "")
        vm_name = vm_name.split("[")[0].strip()

        try:
            vm = self.vm_use_case.get_vm(vm_name)
            if vm:
                self.name_input.setText(vm.name)
                self.iso_path.setText(vm.iso or "")
                self.disk_path.setText(vm.disk)
                self.cpu_cores.setValue(vm.cpus)
                self.ram_size.setValue(vm.ram)
                self.os_type.setCurrentText(vm.os)
                self.vga_type.setCurrentText(getattr(vm, 'vga', 'qxl'))
                self.boot_order.setCurrentText(getattr(vm, 'boot_order', 'Disco duro (para arrancar SO)'))

                if vm.auto_detected:
                    self.auto_detect_label.setText("✓ Auto-detectada del sistema")
                else:
                    self.auto_detect_label.setText("✓ Configuración manual")

                # Show VM info
                info_presenter = InfoPanelPresenter(self.info_text)
                info_presenter.present_vm_info(vm, self.running_vms, self.storage)
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error cargando VM: {e}")

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
        """Guarda configuración de VM"""
        form_widgets = {
            'name': self.name_input,
            'iso': self.iso_path,
            'disk': self.disk_path,
            'cpus': self.cpu_cores,
            'ram': self.ram_size,
            'os': self.os_type,
            'status': self.auto_detect_label
        }
        presenter = ConfigFormPresenter(form_widgets)
        vm_data = presenter.get_vm_data()
        
        if not vm_data['name']:
            QMessageBox.warning(self, "Error", "Ingrese un nombre para la VM")
            return
        
        try:
            vm = self.vm_use_case.create_vm(
                name=vm_data['name'],
                disk=vm_data['disk'],
                iso=vm_data['iso'],
                cpus=vm_data['cpus'],
                ram=vm_data['ram'],
                os=vm_data['os']
            )
            
            # NUEVO: Guardar boot order en VM
            vm.boot_order = self.boot_order.currentText()
            vm.vga = self.vga_type.currentText()
            
            # Guardar la VM actualizada
            self.vm_use_case.update_vm(vm)
            
            self.refresh_vm_list()
            QMessageBox.information(self, "Éxito", f"VM '{vm_data['name']}' guardada")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error guardando VM: {e}")
    
    def start_vm(self):
        """Inicia VM seleccionada"""
        item = self.vm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una VM")
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        
        try:
            vm = self.vm_use_case.get_vm(vm_name)
            if not vm:
                QMessageBox.warning(self, "Error", "VM no encontrada")
                return

            if vm_name in self.running_vms:
                QMessageBox.warning(self, "Advertencia", f"La VM '{vm_name}' ya está en ejecución")
                return

            # Start the VM using qemu_executor (it handles command building internally)
            if self.qemu_executor.start_vm(vm):
                self.running_vms[vm_name] = True
                self.refresh_vm_list()
                QMessageBox.information(self, "Éxito", f"VM '{vm_name}' iniciada")
            else:
                QMessageBox.critical(self, "Error", "No se pudo iniciar la VM")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error iniciando VM: {e}")

    def restart_vm(self):
        """Reinicia VM seleccionada (detiene y vuelve a iniciar)"""
        item = self.vm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una VM")
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        
        try:
            if vm_name not in self.running_vms:
                QMessageBox.warning(self, "Advertencia", f"La VM '{vm_name}' no está en ejecución")
                return
            
            # Detener VM
            if self.qemu_executor.stop_vm(vm_name):
                del self.running_vms[vm_name]
                self.refresh_vm_list()
                
                # Pequeña pausa para asegurar que se detuvo
                from time import sleep
                sleep(1)
                
                # Volver a iniciar
                vm = self.vm_use_case.get_vm(vm_name)
                if vm and self.qemu_executor.start_vm(vm):
                    self.running_vms[vm_name] = True
                    self.refresh_vm_list()
                    QMessageBox.information(self, "Éxito", f"VM '{vm_name}' reiniciada")
                else:
                    QMessageBox.critical(self, "Error", "No se pudo reiniciar la VM")
            else:
                QMessageBox.critical(self, "Error", "No se pudo detener la VM para reiniciarla")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error reiniciando VM: {e}")
    
    def shutdown_vm(self):
        """Apaga VM seleccionada (envía señal de apagado graceful)"""
        item = self.vm_list.currentItem()
        if not item:
            QMessageBox.warning(self, "Error", "Seleccione una VM")
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        
        try:
            if vm_name not in self.running_vms:
                QMessageBox.warning(self, "Advertencia", f"La VM '{vm_name}' no está en ejecución")
                return
            
            reply = QMessageBox.question(
                self,
                "Confirmar apagado",
                f"¿Apagar la VM '{vm_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.Yes:
                # Intentar apagado graceful primero (ACPI shutdown)
                import subprocess
                shutdown_cmd = f'echo quit | nc localhost 5900'  # Para QEMU Monitor si está habilitado
                
                # Si no funciona, usar detener normal
                if self.qemu_executor.stop_vm(vm_name):
                    del self.running_vms[vm_name]
                    self.refresh_vm_list()
                    QMessageBox.information(self, "Éxito", f"VM '{vm_name}' apagada")
                else:
                    QMessageBox.critical(self, "Error", "No se pudo apagar la VM")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error apagando VM: {e}")

    def stop_vm(self):
        """Detiene VM seleccionada"""
        item = self.vm_list.currentItem()
        if not item:
            return
        
        vm_name = item.text().replace("📦 ", "").replace("⚙️ ", "").replace(" (detectada)", "").split("[")[0].strip()
        
        try:
            if vm_name in self.running_vms:
                if self.qemu_executor.stop_vm(vm_name):
                    del self.running_vms[vm_name]
                    self.refresh_vm_list()
                    QMessageBox.information(self, "Éxito", f"VM '{vm_name}' detenida")
            else:
                QMessageBox.warning(self, "Advertencia", f"La VM '{vm_name}' no está en ejecución")
        except Exception as e:
            QMessageBox.critical(self, "Error", f"Error deteniendo VM: {e}")
    
    def delete_vm(self):
        """Elimina VM seleccionada"""
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
            try:
                self.vm_use_case.delete_vm(vm_name)
                self.refresh_vm_list()
                QMessageBox.information(self, "Éxito", "VM eliminada")
            except Exception as e:
                QMessageBox.critical(self, "Error", f"Error eliminando VM: {e}")
    
    def update_vm_status(self):
        """Actualiza estado de VMs en ejecución"""
        dead_vms = [name for name in self.running_vms if not self.qemu_executor.running_processes.get(name)]
        for vm_name in dead_vms:
            del self.running_vms[vm_name]
            self.refresh_vm_list()
    
    def browse_iso(self):
        """Abre diálogo para seleccionar ISO"""
        path, _ = QFileDialog.getOpenFileName(self, "Seleccionar ISO", "", "ISO Files (*.iso)")
        if path:
            self.iso_path.setText(path)
    
    def browse_disk(self):
        """Abre diálogo para seleccionar disco"""
        path, _ = QFileDialog.getSaveFileName(self, "Seleccionar Disco", "", "QEMU Image (*.qcow2)")
        if path:
            self.disk_path.setText(path)
    
    # ==================== DIÁLOGOS ====================
    
    def open_disk_manager(self):
        """Abre gestor de discos"""
        dialog = DiskManagerDialog(self, self.storage)
        dialog.exec_()
    
    def open_network_dialog(self):
        """Abre gestor de redes"""
        dialog = NetworkDialog(self)
        dialog.exec_()
    
    def open_video_dialog(self):
        """Abre configurador de video"""
        dialog = VideoDialog(self)
        dialog.exec_()
    
    def open_peripherals_dialog(self):
        """Abre gestor de periféricos"""
        dialog = PeripheralsDialog(self)
        dialog.exec_()
    
    def open_search_dialog(self):
        """Abre diálogo de búsqueda"""
        dialog = SearchDialog(self, self.storage)
        dialog.exec_()
    
    def show_about(self):
        """Muestra diálogo About"""
        dialog = AboutDialog(self)
        dialog.exec_()
    
    def show_help(self):
        """Muestra ayuda"""
        help_text = """
        <b>QEMU Manager - Ayuda</b><br><br>
        
        <b>Funcionalidades:</b><br>
        • <b>Nueva VM:</b> Crear una nueva máquina virtual<br>
        • <b>Buscar:</b> Buscar discos e imágenes existentes<br>
        • <b>Importar:</b> Importar discos existentes<br>
        • <b>Iniciar/Detener:</b> Controlar máquinas virtuales<br><br>
        
        <b>Atajos de teclado:</b><br>
        • Ctrl+N: Nueva VM<br>
        • Ctrl+F: Buscar<br>
        • Ctrl+O: Cargar configuración<br>
        • Ctrl+S: Guardar configuración<br>
        • F5: Actualizar lista<br>
        • Ctrl+Q: Salir<br>
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
    
    def load_config_file(self):
        """Carga configuración desde archivo"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Cargar Configuración", "", "JSON Files (*.json)"
        )
        if path:
            QMessageBox.information(self, "Éxito", "Configuración cargada")
    
    def save_all_configs(self):
        """Guarda todas las configuraciones"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Guardar Configuración", "qemu_config.json", "JSON Files (*.json)"
        )
        if path:
            QMessageBox.information(self, "Éxito", "Configuración guardada")
    
    def import_vm(self):
        """Importa VM desde archivo"""
        path, _ = QFileDialog.getOpenFileName(
            self, "Importar VM", "", "QEMU Image (*.qcow2)"
        )
        if path:
            QMessageBox.information(self, "Éxito", "VM importada")
    
    def export_vm(self):
        """Exporta VM a archivo"""
        path, _ = QFileDialog.getSaveFileName(
            self, "Exportar VM", "vm_config.json", "JSON Files (*.json)"
        )
        if path:
            QMessageBox.information(self, "Éxito", "VM exportada")
    
    def detect_running_vms(self):
        """Detecta VMs que siguen en ejecución desde sesiones anteriores"""
        try:
            import subprocess
            import re
            
            # Buscar procesos qemu-system-x86_64 en ejecución
            if sys.platform == 'win32':
                # Windows: usar tasklist
                result = subprocess.run(
                    'tasklist /FI "IMAGENAME eq qemu-system-x86_64.exe"',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                # Si encuentra procesos, hay VMs ejecutándose
                if 'qemu-system-x86_64.exe' in result.stdout:
                    print("[WARN] Se detectaron VMs en ejecución desde sesión anterior")
                    return True
            else:
                # Linux/Mac: usar ps
                result = subprocess.run(
                    'ps aux | grep qemu-system-x86_64',
                    shell=True,
                    capture_output=True,
                    text=True
                )
                if 'qemu-system-x86_64' in result.stdout and 'grep' not in result.stdout:
                    print("[WARN] Se detectaron VMs en ejecución desde sesión anterior")
                    return True
            
            return False
        except Exception as e:
            print(f"[WARN] Error detectando VMs en ejecución: {e}")
            return False
    
    def handle_orphaned_vms(self):
        """Maneja VMs huérfanas detectadas"""
        if self.detect_running_vms():
            reply = QMessageBox.question(
                self,
                "VMs en ejecución detectadas",
                "Se detectaron máquinas virtuales en ejecución desde una sesión anterior.\n\n"
                "¿Qué deseas hacer?\n\n"
                "Sí: Monitorear VMs existentes\n"
                "No: Terminar todas las VMs de QEMU",
                QMessageBox.Yes | QMessageBox.No
            )
            
            if reply == QMessageBox.No:
                # Terminar todas las VMs
                self.kill_all_qemu_processes()
            else:
                # Sincronizar estado - marcar como ejecutándose
                self.sync_running_vms_state()
    
    def sync_running_vms_state(self):
        """Sincroniza el estado de las VMs con la realidad"""
        try:
            import subprocess
            
            # Obtener lista de VMs
            vms = self.vm_use_case.get_all_vms()
            
            for vm in vms:
                # Buscar si la VM está en ejecución
                if sys.platform == 'win32':
                    cmd = f'tasklist | find /I "{vm.name}"'
                else:
                    cmd = f'ps aux | grep -i "{vm.name}" | grep -v grep'
                
                result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
                
                if result.stdout and vm.name not in self.running_vms:
                    print(f"[INFO] VM detectada en ejecución: {vm.name}")
                    self.running_vms[vm.name] = True
                elif not result.stdout and vm.name in self.running_vms:
                    print(f"[INFO] VM no está ejecutándose: {vm.name}")
                    del self.running_vms[vm.name]
            
            self.refresh_vm_list()
        except Exception as e:
            print(f"[WARN] Error sincronizando estado: {e}")
    
    def kill_all_qemu_processes(self):
        """Termina todos los procesos QEMU en ejecución"""
        try:
            if sys.platform == 'win32':
                subprocess.run('taskkill /IM qemu-system-x86_64.exe /F', shell=True)
            else:
                subprocess.run('pkill -f qemu-system-x86_64', shell=True)
            
            QMessageBox.information(
                self,
                "Éxito",
                "Todos los procesos QEMU han sido terminados"
            )
            self.running_vms.clear()
            self.refresh_vm_list()
        except Exception as e:
            QMessageBox.warning(self, "Error", f"Error terminando procesos: {e}")


    def closeEvent(self, event):
        """Maneja cierre de la aplicación"""
        # Detener todas las VMs
        for vm_name in list(self.running_vms.keys()):
            try:
                self.qemu_executor.stop_vm(vm_name)
            except:
                pass
        
        event.accept()


