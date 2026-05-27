"""Linux platform adapter using iproute2."""

import json
import re
import subprocess
from typing import List, Optional

from .base import NetworkInterface, PlatformAdapter


class LinuxAdapter(PlatformAdapter):
    """Adapter for Linux network operations."""

    def _run(self, cmd: List[str], check: bool = True) -> str:
        result = subprocess.run(cmd, capture_output=True, text=True, check=check)
        return result.stdout

    def list_interfaces(self) -> List[NetworkInterface]:
        try:
            stdout = self._run(["ip", "-j", "addr", "show"])
            data = json.loads(stdout)
        except Exception:
            stdout = self._run(["ip", "addr", "show"])
            data = self._parse_ip_addr(stdout)

        interfaces = []
        for entry in data:
            name = entry.get("ifname", "")
            alias = name
            mac = entry.get("address")
            state = entry.get("operstate")
            ip = None
            mask = None

            for addr_info in entry.get("addr_info", []):
                if addr_info.get("family") == "inet":
                    ip = addr_info.get("local")
                    prefix = addr_info.get("prefixlen")
                    if prefix:
                        mask = self.cidr_to_mask(prefix)
                    break

            iface = NetworkInterface(name=name, alias=alias, mac=mac, ip=ip, mask=mask, status=state)
            interfaces.append(iface)

        return interfaces

    def _parse_ip_addr(self, stdout: str) -> List[dict]:
        """Fallback parser for non-JSON ip addr output."""
        entries = []
        current = {}
        for line in stdout.splitlines():
            m = re.match(r"^(\d+):\s+(\S+):.*state\s+(\S+)", line)
            if m:
                if current:
                    entries.append(current)
                current = {"ifname": m.group(2), "operstate": m.group(3), "addr_info": []}
            mac_m = re.search(r"link/ether\s+([0-9a-f:]+)", line)
            if mac_m and current:
                current["address"] = mac_m.group(1)
            inet_m = re.search(r"inet\s+([\d.]+)/(\d+)", line)
            if inet_m and current:
                current["addr_info"].append({"family": "inet", "local": inet_m.group(1), "prefixlen": int(inet_m.group(2))})
        if current:
            entries.append(current)
        return entries

    def set_subnet_mask(self, interface_name: str, ip: str, mask: str, gateway: Optional[str] = None) -> None:
        prefix = self.mask_to_cidr(mask)
        # Remove existing IPv4 addresses
        self._run(["ip", "addr", "flush", "dev", interface_name, "label", f"{interface_name}:0"], check=False)
        self._run(["ip", "addr", "add", f"{ip}/{prefix}", "dev", interface_name])
        if gateway:
            self._run(["ip", "route", "add", "default", "via", gateway, "dev", interface_name], check=False)

    def set_dhcp(self, interface_name: str) -> None:
        # Attempt dhclient; user may need to install/use their distro's network manager
        self._run(["dhclient", "-r", interface_name], check=False)
        self._run(["dhclient", interface_name], check=False)
