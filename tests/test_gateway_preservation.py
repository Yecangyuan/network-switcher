import unittest

from network_switcher.platforms.linux import LinuxAdapter
from network_switcher.platforms.macos import MacOSAdapter
from network_switcher.platforms.windows import WindowsAdapter


class RecordingMacOSAdapter(MacOSAdapter):
    def __init__(self) -> None:
        self.calls = []

    def _run(self, cmd, check=True):
        self.calls.append((cmd, check))
        if cmd == ["networksetup", "-listallhardwareports"]:
            return (
                "Hardware Port: USB 10/100/1000 LAN\n"
                "Device: en7\n"
                "Ethernet Address: aa:bb:cc:dd:ee:ff\n"
            )
        if cmd == ["ipconfig", "getifaddr", "en7"]:
            return "192.168.1.20\n"
        if cmd == ["networksetup", "-getinfo", "USB 10/100/1000 LAN"]:
            return (
                "IP address: 192.168.1.20\n"
                "Subnet mask: 255.255.255.0\n"
                "Router: 192.168.1.1\n"
            )
        return ""


class RecordingWindowsAdapter(WindowsAdapter):
    def __init__(self) -> None:
        self.calls = []

    def _run(self, cmd, shell=False, check=True):
        self.calls.append((cmd, shell, check))
        if cmd[:2] == ["powershell", "-NoProfile"] and "Get-NetRoute" in cmd[-1]:
            return "192.168.1.1\n"
        return ""


class RecordingLinuxAdapter(LinuxAdapter):
    def __init__(self) -> None:
        self.calls = []

    def _run(self, cmd, check=True):
        self.calls.append((cmd, check))
        if cmd == ["ip", "route", "show", "default", "dev", "eth0"]:
            return "default via 192.168.1.1 dev eth0 proto dhcp metric 100\n"
        return ""


class GatewayPreservationTests(unittest.TestCase):
    def test_macos_reuses_current_router_when_gateway_is_omitted(self) -> None:
        adapter = RecordingMacOSAdapter()

        adapter.set_subnet_mask("en7", "192.168.1.30", "255.255.255.0")

        self.assertIn(
            (
                [
                    "networksetup",
                    "-setmanual",
                    "USB 10/100/1000 LAN",
                    "192.168.1.30",
                    "255.255.255.0",
                    "192.168.1.1",
                ],
                True,
            ),
            adapter.calls,
        )

    def test_windows_reuses_current_default_gateway_when_gateway_is_omitted(self) -> None:
        adapter = RecordingWindowsAdapter()

        adapter.set_subnet_mask("Ethernet", "192.168.1.30", "255.255.255.0")

        self.assertIn(
            (
                [
                    "netsh",
                    "interface",
                    "ip",
                    "set",
                    "address",
                    'name="Ethernet"',
                    "static",
                    "192.168.1.30",
                    "255.255.255.0",
                    "192.168.1.1",
                ],
                True,
                True,
            ),
            adapter.calls,
        )

    def test_linux_reuses_current_default_gateway_when_gateway_is_omitted(self) -> None:
        adapter = RecordingLinuxAdapter()

        adapter.set_subnet_mask("eth0", "192.168.1.30", "255.255.255.0")

        self.assertIn(
            (
                [
                    "ip",
                    "route",
                    "replace",
                    "default",
                    "via",
                    "192.168.1.1",
                    "dev",
                    "eth0",
                ],
                False,
            ),
            adapter.calls,
        )


if __name__ == "__main__":
    unittest.main()
