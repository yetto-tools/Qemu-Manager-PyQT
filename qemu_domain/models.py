# ==================== DOMAIN LAYER ====================
# qemu_domain/models.py

from dataclasses import dataclass
from typing import List, Optional
from enum import Enum


class VMStatus(Enum):
    STOPPED = "stopped"
    RUNNING = "running"
    PAUSED = "paused"


class DiskFormat(Enum):
    QCOW2 = "qcow2"
    RAW = "raw"
    VDI = "vdi"
    VMDK = "vmdk"


@dataclass
class VirtualMachine:
    name: str
    disk: str
    iso: Optional[str] = None
    cpus: int = 2
    ram: int = 1024
    os: str = "Linux"
    status: VMStatus = VMStatus.STOPPED
    auto_detected: bool = False


@dataclass
class VirtualDisk:
    name: str
    path: str
    size_gb: float
    format: DiskFormat
    location: str


@dataclass
class Network:
    name: str
    network_type: str  # user, bridge, tap, vde
    subnet: str
    dhcp_enabled: bool
    ipv6_enabled: bool


@dataclass
class VideoConfig:
    vga_type: str  # qxl, virtio, vmware, vga, cirrus, std
    resolution: str
    vram_mb: int
    gl_acceleration: bool
    virgl: bool
    monitors: int


@dataclass
class AudioConfig:
    enabled: bool
    driver: str  # pulseaudio, alsa, oss
    model: str  # ac97, es1370, sb16, hdmi
    volume: int


@dataclass
class USBConfig:
    version: str  # 1.1, 2.0, 3.0, 3.1
    ports: int
    redirect_enabled: bool


