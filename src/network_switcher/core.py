"""Core logic for detecting platform and executing network operations."""

import platform
import sys
from typing import Optional

from .platforms.base import NetworkInterface, PlatformAdapter
from .platforms.windows import WindowsAdapter
from .platforms.macos import MacOSAdapter
from .platforms.linux import LinuxAdapter


def get_adapter() -> PlatformAdapter:
    """Return the appropriate platform adapter."""
    system = platform.system().lower()
    if system == "windows":
        return WindowsAdapter()
    if system == "darwin":
        return MacOSAdapter()
    if system == "linux":
        return LinuxAdapter()
    raise RuntimeError(f"Unsupported platform: {system}")


def list_interfaces() -> list[NetworkInterface]:
    """List all network interfaces."""
    adapter = get_adapter()
    return adapter.list_interfaces()


def set_static(interface_name: str, ip: str, mask: str, gateway: Optional[str] = None) -> None:
    """Set static IP and subnet mask for an interface."""
    adapter = get_adapter()
    adapter.set_subnet_mask(interface_name, ip, mask, gateway)


def set_dhcp(interface_name: str) -> None:
    """Enable DHCP on an interface."""
    adapter = get_adapter()
    adapter.set_dhcp(interface_name)
