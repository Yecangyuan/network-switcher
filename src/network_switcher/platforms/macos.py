"""macOS platform adapter using networksetup."""

import re
import subprocess
from typing import List, Optional

from .base import NetworkInterface, PlatformAdapter


class MacOSAdapter(PlatformAdapter):
    """Adapter for macOS network operations."""

    def _run(self, cmd: List[str], check: bool = True) -> str:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result.stdout

    def list_interfaces(self) -> List[NetworkInterface]:
        stdout = self._run(["networksetup", "-listallhardwareports"])
        blocks = stdout.strip().split("\n\n")
        interfaces = []

        for block in blocks:
            name_match = re.search(r"^Hardware Port:\s*(.+)$", block, re.MULTILINE)
            device_match = re.search(r"^Device:\s*(.+)$", block, re.MULTILINE)
            mac_match = re.search(r"^Ethernet Address:\s*(.+)$", block, re.MULTILINE)

            if device_match:
                alias = name_match.group(1).strip() if name_match else device_match.group(1).strip()
                device = device_match.group(1).strip()
                mac = mac_match.group(1).strip() if mac_match else None

                ip = None
                mask = None
                try:
                    info = self._run(["ipconfig", "getifaddr", device], check=False).strip()
                    if info:
                        ip = info
                except Exception:
                    pass

                iface = NetworkInterface(name=device, alias=alias, mac=mac, ip=ip, mask=mask)
                interfaces.append(iface)

        return interfaces

    def set_subnet_mask(self, interface_name: str, ip: str, mask: str, gateway: Optional[str] = None) -> None:
        alias = self._resolve_alias(interface_name)
        if gateway is None:
            gateway = self._get_current_gateway(alias)
        cmd = ["networksetup", "-setmanual", alias, ip, mask]
        if gateway:
            cmd.append(gateway)
        self._run(cmd)

    def set_dhcp(self, interface_name: str) -> None:
        alias = self._resolve_alias(interface_name)
        self._run(["networksetup", "-setdhcp", alias])

    def _resolve_alias(self, name: str) -> str:
        for iface in self.list_interfaces():
            if iface.name == name or iface.alias == name:
                return iface.alias
        return name

    def _get_current_gateway(self, alias: str) -> Optional[str]:
        info = self._run(["networksetup", "-getinfo", alias], check=False)
        match = re.search(r"^Router:\s*(.+)$", info, re.MULTILINE)
        if not match:
            return None

        gateway = match.group(1).strip()
        if not gateway or gateway.lower() in {"none", "not set", "(null)", "-"}:
            return None
        return gateway
