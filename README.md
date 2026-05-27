# Network Switcher

A lightweight, cross-platform GUI/CLI tool for switching ethernet subnet masks and IP configurations. Primarily optimized for **Windows 10**, with full support for **macOS** and **Linux**.

## Features

- **Cross-platform**: Windows 10, macOS, Linux
- **GUI mode**: Easy-to-use Tkinter interface (no extra dependencies)
- **CLI mode**: Full command-line support for scripting
- **List interfaces**: Display all network interfaces with IP, MAC, mask, and status
- **Set static IP**: Configure static IP and subnet mask
- **DHCP mode**: Switch back to DHCP easily
- **Zero dependencies**: Uses only Python standard library

## Installation

```bash
pip install -e .
```

Or run directly:

```bash
python -m network_switcher list
```

## Usage

### GUI Mode

Launch the graphical interface (requires a display):

```bash
network-switcher-gui
```

GUI features:
- **Interface list**: Browse all network adapters in a sortable table
- **One-click select**: Click any row to auto-fill the interface name
- **Set Static IP**: Enter IP, mask, and optional gateway, then click "Set Static IP"
- **Enable DHCP**: Click "Enable DHCP" to switch the selected interface to DHCP
- **Refresh**: Reload the interface list after making changes

> **Note**: On Windows, right-click and "Run as administrator". On macOS/Linux, prefix with `sudo`.

### CLI Mode

### List network interfaces

```bash
network-switcher list
```

Example output:

```
Name                 Alias                IP               Mask             MAC                Status
----------------------------------------------------------------------------------------------------
Ethernet             Ethernet             192.168.1.100    255.255.255.0    AA:BB:CC:DD:EE:FF  Up
Wi-Fi                Wi-Fi                192.168.1.101    255.255.255.0    11:22:33:44:55:66  Up
```

### Set static IP and subnet mask

```bash
# Windows (run as Administrator)
network-switcher set "Ethernet" --ip 192.168.1.50 --mask 255.255.255.0 --gateway 192.168.1.1

# macOS / Linux (run with sudo)
sudo network-switcher set en0 --ip 192.168.1.50 --mask 255.255.255.0 --gateway 192.168.1.1
```

### Enable DHCP

```bash
# Windows (run as Administrator)
network-switcher dhcp "Ethernet"

# macOS / Linux (run with sudo)
sudo network-switcher dhcp en0
```

## Platform Notes

| Platform | Requirements |
|----------|-------------|
| Windows 10 | Administrator privileges; uses `netsh` and PowerShell |
| macOS | `networksetup` (built-in); may require `sudo` |
| Linux | `iproute2` (`ip` command); may require `sudo` |

## Project Structure

```
src/network_switcher/
├── __init__.py
├── __main__.py       # python -m entry point
├── cli.py            # Command-line interface
├── gui.py            # Tkinter graphical interface
├── core.py           # Platform detection and routing
└── platforms/
    ├── base.py       # Abstract base adapter
    ├── windows.py    # Windows implementation (netsh / PowerShell)
    ├── macos.py      # macOS implementation (networksetup)
    └── linux.py      # Linux implementation (iproute2)
```

## License

MIT
