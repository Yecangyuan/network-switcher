"""Command-line interface for the network switcher."""

import argparse
import sys

from . import __version__
from .core import list_interfaces, set_static, set_dhcp


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        prog="network-switcher",
        description="Cross-platform CLI tool to switch ethernet subnet masks.",
    )
    parser.add_argument("--version", action="version", version=f"%(prog)s {__version__}")

    subparsers = parser.add_subparsers(dest="command", help="Available commands")

    # list
    subparsers.add_parser("list", help="List network interfaces")

    # set
    set_parser = subparsers.add_parser("set", help="Set static IP and subnet mask")
    set_parser.add_argument("interface", help="Network interface name or alias")
    set_parser.add_argument("--ip", required=True, help="Static IP address")
    set_parser.add_argument("--mask", required=True, help="Subnet mask (e.g., 255.255.255.0)")
    set_parser.add_argument("--gateway", help="Default gateway (optional; preserves current gateway if omitted)")

    # dhcp
    dhcp_parser = subparsers.add_parser("dhcp", help="Enable DHCP on interface")
    dhcp_parser.add_argument("interface", help="Network interface name or alias")

    return parser


def print_interfaces() -> None:
    interfaces = list_interfaces()
    if not interfaces:
        print("No network interfaces found.")
        return

    print(f"{'Name':<20} {'Alias':<20} {'IP':<16} {'Mask':<16} {'MAC':<18} {'Status'}")
    print("-" * 100)
    for iface in interfaces:
        print(
            f"{iface.name:<20} {iface.alias:<20} {iface.ip or '-':<16} "
            f"{iface.mask or '-':<16} {iface.mac or '-':<18} {iface.status or '-'}"
        )


def main(argv: list[str] | None = None) -> int:
    parser = create_parser()
    args = parser.parse_args(argv)

    if args.command is None:
        parser.print_help()
        return 0

    try:
        if args.command == "list":
            print_interfaces()
        elif args.command == "set":
            set_static(args.interface, args.ip, args.mask, args.gateway)
            print(f"Successfully set {args.interface} to {args.ip}/{args.mask}")
        elif args.command == "dhcp":
            set_dhcp(args.interface)
            print(f"Successfully enabled DHCP on {args.interface}")
    except PermissionError:
        print("Error: Administrator/root privileges required to modify network settings.", file=sys.stderr)
        return 1
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        return 1

    return 0
