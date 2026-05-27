"""Windows platform adapter using netsh and PowerShell."""

import re
import subprocess
from typing import List, Optional

from .base import NetworkInterface, PlatformAdapter


class WindowsAdapter(PlatformAdapter):
    """Adapter for Windows network operations."""

    def _run(self, cmd: List[str], shell: bool = False, check: bool = True) -> str:
        result = subprocess.run(cmd, capture_output=True, text=True, shell=shell, check=check)
        return result.stdout

    def list_interfaces(self) -> List[NetworkInterface]:
        stdout = self._run(["netsh", "interface", "show", "interface"])
        lines = stdout.strip().splitlines()
        interfaces = []

        # Skip header lines (first 2 or 3 lines)
        data_lines = [l for l in lines if l.strip() and not l.strip().startswith("-") and "Admin State" not in l]

        for line in data_lines:
            parts = line.strip().split(None, 3)
            if len(parts) >= 4:
                status, iface_type, conn_state, name = parts[0], parts[1], parts[2], parts[3]
                iface = NetworkInterface(name=name, alias=name, status=conn_state)
                interfaces.append(iface)

        # Enrich with IP/MAC via PowerShell
        try:
            ps_cmd = (
                "Get-NetAdapter | Select-Object Name,MacAddress,InterfaceOperationalStatus | "
                "ConvertTo-Csv -NoTypeInformation"
            )
            ps_out = self._run(["powershell", "-Command", ps_cmd], check=False)
            mac_map = {}
            for line in ps_out.strip().splitlines()[1:]:
                cols = line.strip().split(",")
                if len(cols) >= 2:
                    raw_name = cols[0].strip('"')
                    raw_mac = cols[1].strip('"')
                    mac_map[raw_name] = raw_mac

            ps_ip = (
                "Get-NetIPAddress -AddressFamily IPv4 | "
                "Select-Object InterfaceAlias,IPAddress,PrefixLength | ConvertTo-Csv -NoTypeInformation"
            )
            ps_ip_out = self._run(["powershell", "-Command", ps_ip], check=False)
            ip_map = {}
            prefix_map = {}
            for line in ps_ip_out.strip().splitlines()[1:]:
                cols = line.strip().split(",")
                if len(cols) >= 3:
                    alias = cols[0].strip('"')
                    ip = cols[1].strip('"')
                    prefix = cols[2].strip('"')
                    ip_map[alias] = ip
                    prefix_map[alias] = prefix

            for iface in interfaces:
                iface.mac = mac_map.get(iface.name)
                iface.ip = ip_map.get(iface.name)
                prefix = prefix_map.get(iface.name)
                if prefix:
                    iface.mask = self.cidr_to_mask(int(prefix))
        except Exception:
            pass

        return interfaces

    def set_subnet_mask(self, interface_name: str, ip: str, mask: str, gateway: Optional[str] = None) -> None:
        cmd = [
            "netsh",
            "interface",
            "ip",
            "set",
            "address",
            f'name="{interface_name}"',
            "static",
            ip,
            mask,
        ]
        if gateway:
            cmd.append(gateway)
        self._run(cmd, shell=True)

    def set_dhcp(self, interface_name: str) -> None:
        self._run(
            ["netsh", "interface", "ip", "set", "address", f'name="{interface_name}"', "dhcp"],
            shell=True,
        )
