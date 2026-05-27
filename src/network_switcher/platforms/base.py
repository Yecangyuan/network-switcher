"""Base adapter for network interface operations."""

from abc import ABC, abstractmethod
from dataclasses import dataclass
from typing import List, Optional


@dataclass
class NetworkInterface:
    """Represents a network interface."""

    name: str
    alias: str
    mac: Optional[str] = None
    ip: Optional[str] = None
    mask: Optional[str] = None
    status: Optional[str] = None


class PlatformAdapter(ABC):
    """Abstract base for platform-specific network operations."""

    @abstractmethod
    def list_interfaces(self) -> List[NetworkInterface]:
        """Return list of network interfaces."""

    @abstractmethod
    def set_subnet_mask(self, interface_name: str, ip: str, mask: str, gateway: Optional[str] = None) -> None:
        """Set static IP with subnet mask for given interface."""

    @abstractmethod
    def set_dhcp(self, interface_name: str) -> None:
        """Configure interface to use DHCP."""

    @staticmethod
    def mask_to_cidr(mask: str) -> int:
        """Convert dotted-decimal subnet mask to CIDR prefix length."""
        parts = [int(x) for x in mask.split(".")]
        binary = sum(bin(x).count("1") for x in parts)
        return binary

    @staticmethod
    def cidr_to_mask(prefix: int) -> str:
        """Convert CIDR prefix length to dotted-decimal subnet mask."""
        bits = 0xFFFFFFFF ^ (0xFFFFFFFF >> prefix)
        return ".".join(str((bits >> i) & 0xFF) for i in [24, 16, 8, 0])
