"""Small GUI helpers that do not depend on Tk."""

GATEWAY_HELP_TEXT = "Leave blank to preserve the current gateway when possible."


def format_interface_summary(name: str, alias: str, ip: str, mask: str, mac: str, status: str) -> str:
    """Return a compact single-line interface summary."""
    values = [name, alias, ip, mask, mac, status]
    return " | ".join(value or "-" for value in values)
