"""Tkinter GUI for the network switcher."""

import tkinter as tk
from tkinter import messagebox, ttk
from typing import Optional

from . import __version__
from .core import list_interfaces, set_dhcp, set_static
from .gui_helpers import GATEWAY_HELP_TEXT, GUI_TEXT, format_interface_summary


COLORS = {
    "app_bg": "#eef6f4",
    "surface": "#ffffff",
    "surface_alt": "#f6fbfa",
    "primary": "#0f766e",
    "primary_dark": "#115e59",
    "accent": "#f97316",
    "text": "#12312f",
    "muted": "#56706c",
    "border": "#cde3df",
    "success": "#047857",
    "danger": "#b91c1c",
}


class NetworkSwitcherGUI:
    """Cross-platform GUI for switching ethernet subnet masks."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title(GUI_TEXT["window_title"])
        self.root.geometry("980x680")
        self.root.minsize(820, 560)
        self.root.configure(bg=COLORS["app_bg"])

        self.status_var = tk.StringVar(value=GUI_TEXT["ready"])
        self.summary_var = tk.StringVar(value=GUI_TEXT["no_interface_selected"])
        self.detail_vars = {
            "name": tk.StringVar(value="-"),
            "alias": tk.StringVar(value="-"),
            "ip": tk.StringVar(value="-"),
            "mask": tk.StringVar(value="-"),
            "mac": tk.StringVar(value="-"),
            "status": tk.StringVar(value="-"),
        }

        self._configure_style()
        self._build_ui()
        self.refresh_interfaces()

    def _configure_style(self) -> None:
        self.style = ttk.Style(self.root)
        try:
            if "clam" in self.style.theme_names():
                self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.root.option_add("*Font", "{Segoe UI} 10")

        self.style.configure("App.TFrame", background=COLORS["app_bg"])
        self.style.configure("Surface.TFrame", background=COLORS["surface"])
        self.style.configure("Header.TFrame", background=COLORS["primary"])
        self.style.configure("Actions.TFrame", background=COLORS["surface"])

        self.style.configure(
            "Card.TLabelframe",
            background=COLORS["surface"],
            bordercolor=COLORS["border"],
            relief=tk.SOLID,
        )
        self.style.configure(
            "Card.TLabelframe.Label",
            background=COLORS["surface"],
            foreground=COLORS["primary_dark"],
            font=("{Segoe UI}", 10, "bold"),
        )

        self.style.configure("Title.TLabel", background=COLORS["primary"], foreground="#ffffff", font=("{Segoe UI}", 20, "bold"))
        self.style.configure("Subtitle.TLabel", background=COLORS["primary"], foreground="#d5f5ef", font=("{Segoe UI}", 10))
        self.style.configure("Pill.TLabel", background=COLORS["primary_dark"], foreground="#ffffff", font=("{Segoe UI}", 9, "bold"))
        self.style.configure("Label.TLabel", background=COLORS["surface"], foreground=COLORS["muted"])
        self.style.configure("Value.TLabel", background=COLORS["surface"], foreground=COLORS["text"], font=("{Segoe UI}", 10, "bold"))
        self.style.configure("Hint.TLabel", background=COLORS["surface"], foreground=COLORS["muted"], font=("{Segoe UI}", 9))
        self.style.configure("Summary.TLabel", background=COLORS["surface_alt"], foreground=COLORS["text"], font=("{Segoe UI}", 10, "bold"))
        self.style.configure("Footer.TLabel", background=COLORS["primary_dark"], foreground="#ffffff", padding=(12, 6))

        self.style.configure("TEntry", padding=(8, 5), fieldbackground="#ffffff")
        self.style.configure("TButton", padding=(12, 7), font=("{Segoe UI}", 10, "bold"))
        self.style.configure("Primary.TButton", foreground="#ffffff", background=COLORS["primary"])
        self.style.map("Primary.TButton", background=[("active", COLORS["primary_dark"])])
        self.style.configure("Accent.TButton", foreground="#ffffff", background=COLORS["accent"])
        self.style.map("Accent.TButton", background=[("active", "#ea580c")])
        self.style.configure("Secondary.TButton", foreground=COLORS["text"], background="#e0f2f1")
        self.style.map("Secondary.TButton", background=[("active", "#ccfbf1")])

        self.style.configure(
            "Treeview",
            background=COLORS["surface"],
            fieldbackground=COLORS["surface"],
            foreground=COLORS["text"],
            bordercolor=COLORS["border"],
            rowheight=30,
        )
        self.style.configure(
            "Treeview.Heading",
            background="#d9f1ed",
            foreground=COLORS["primary_dark"],
            font=("{Segoe UI}", 10, "bold"),
            relief=tk.FLAT,
        )
        self.style.map("Treeview", background=[("selected", COLORS["primary"])], foreground=[("selected", "#ffffff")])

    def _build_ui(self) -> None:
        shell = ttk.Frame(self.root, style="App.TFrame", padding=18)
        shell.pack(fill=tk.BOTH, expand=True)

        self._build_header(shell)
        self._build_interface_table(shell)
        self._build_details_and_config(shell)

        status_bar = ttk.Label(shell, textvariable=self.status_var, style="Footer.TLabel", anchor=tk.W)
        status_bar.pack(fill=tk.X, pady=(12, 0))

    def _build_header(self, parent: ttk.Frame) -> None:
        header = ttk.Frame(parent, style="Header.TFrame", padding=(18, 14))
        header.pack(fill=tk.X, pady=(0, 14))
        header.columnconfigure(0, weight=1)

        title = ttk.Label(header, text=GUI_TEXT["header_title"], style="Title.TLabel")
        title.grid(row=0, column=0, sticky=tk.W)

        subtitle = ttk.Label(
            header,
            text=GUI_TEXT["header_subtitle"],
            style="Subtitle.TLabel",
        )
        subtitle.grid(row=1, column=0, sticky=tk.W, pady=(3, 0))

        version = ttk.Label(header, text=f"v{__version__}", style="Pill.TLabel", padding=(10, 4))
        version.grid(row=0, column=1, rowspan=2, sticky=tk.E)

    def _build_interface_table(self, parent: ttk.Frame) -> None:
        list_frame = ttk.LabelFrame(parent, text=GUI_TEXT["interfaces_title"], style="Card.TLabelframe", padding=12)
        list_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 12))
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        columns = ("name", "alias", "ip", "mask", "mac", "status")
        self.tree = ttk.Treeview(list_frame, columns=columns, show="headings", selectmode="browse")
        headings = {
            "name": GUI_TEXT["device_column"],
            "alias": GUI_TEXT["service_column"],
            "ip": GUI_TEXT["ip_column"],
            "mask": GUI_TEXT["mask_column"],
            "mac": GUI_TEXT["mac_column"],
            "status": GUI_TEXT["status_column"],
        }
        widths = {
            "name": 120,
            "alias": 170,
            "ip": 130,
            "mask": 130,
            "mac": 160,
            "status": 90,
        }

        for column in columns:
            self.tree.heading(column, text=headings[column])
            self.tree.column(column, width=widths[column], minwidth=80, anchor=tk.W)

        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")

        self.tree.tag_configure("even", background=COLORS["surface"])
        self.tree.tag_configure("odd", background=COLORS["surface_alt"])
        self.tree.bind("<<TreeviewSelect>>", self._on_select)

    def _build_details_and_config(self, parent: ttk.Frame) -> None:
        lower = ttk.Frame(parent, style="App.TFrame")
        lower.pack(fill=tk.X)
        lower.columnconfigure(0, weight=1)
        lower.columnconfigure(1, weight=2)

        self._build_details_panel(lower)
        self._build_config_panel(lower)

    def _build_details_panel(self, parent: ttk.Frame) -> None:
        details = ttk.LabelFrame(parent, text=GUI_TEXT["selected_title"], style="Card.TLabelframe", padding=12)
        details.grid(row=0, column=0, sticky="nsew", padx=(0, 8))
        details.columnconfigure(1, weight=1)

        summary = ttk.Label(details, textvariable=self.summary_var, style="Summary.TLabel", padding=(10, 8), anchor=tk.W)
        summary.grid(row=0, column=0, columnspan=2, sticky="ew", pady=(0, 10))

        rows = [
            (GUI_TEXT["device_label"], "name"),
            (GUI_TEXT["service_label"], "alias"),
            (GUI_TEXT["ip_label"], "ip"),
            (GUI_TEXT["mask_label"], "mask"),
            (GUI_TEXT["mac_label"], "mac"),
            (GUI_TEXT["status_label"], "status"),
        ]
        for index, (label, key) in enumerate(rows, start=1):
            ttk.Label(details, text=f"{label}:", style="Label.TLabel").grid(row=index, column=0, sticky=tk.W, pady=2)
            ttk.Label(details, textvariable=self.detail_vars[key], style="Value.TLabel").grid(
                row=index,
                column=1,
                sticky=tk.W,
                padx=(10, 0),
                pady=2,
            )

    def _build_config_panel(self, parent: ttk.Frame) -> None:
        config = ttk.LabelFrame(parent, text=GUI_TEXT["configuration_title"], style="Card.TLabelframe", padding=12)
        config.grid(row=0, column=1, sticky="nsew", padx=(8, 0))
        config.columnconfigure(1, weight=1)
        config.columnconfigure(3, weight=1)

        ttk.Label(config, text=GUI_TEXT["ip_required_label"], style="Label.TLabel").grid(row=0, column=0, sticky=tk.W, padx=(0, 8), pady=5)
        self.entry_ip = ttk.Entry(config, width=22)
        self.entry_ip.grid(row=0, column=1, sticky="ew", padx=(0, 14), pady=5)

        ttk.Label(config, text=GUI_TEXT["mask_required_label"], style="Label.TLabel").grid(row=0, column=2, sticky=tk.W, padx=(0, 8), pady=5)
        self.entry_mask = ttk.Entry(config, width=22)
        self.entry_mask.insert(0, "255.255.255.0")
        self.entry_mask.grid(row=0, column=3, sticky="ew", pady=5)

        ttk.Label(config, text=GUI_TEXT["gateway_label"], style="Label.TLabel").grid(row=1, column=0, sticky=tk.W, padx=(0, 8), pady=5)
        self.entry_gateway = ttk.Entry(config, width=22)
        self.entry_gateway.grid(row=1, column=1, sticky="ew", padx=(0, 14), pady=5)

        hint = ttk.Label(config, text=GATEWAY_HELP_TEXT, style="Hint.TLabel")
        hint.grid(row=1, column=2, columnspan=2, sticky=tk.W, pady=5)

        actions = ttk.Frame(config, style="Actions.TFrame")
        actions.grid(row=2, column=0, columnspan=4, sticky="ew", pady=(12, 0))
        for column in range(5):
            actions.columnconfigure(column, weight=1)

        ttk.Button(actions, text=GUI_TEXT["refresh_button"], command=self.refresh_interfaces, style="Secondary.TButton").grid(row=0, column=0, sticky="ew", padx=(0, 6))
        ttk.Button(actions, text=GUI_TEXT["set_static_button"], command=self._set_static, style="Primary.TButton").grid(row=0, column=1, sticky="ew", padx=6)
        ttk.Button(actions, text=GUI_TEXT["switch_16_button"], command=lambda: self._apply_mask("255.255.0.0"), style="Accent.TButton").grid(row=0, column=2, sticky="ew", padx=6)
        ttk.Button(actions, text=GUI_TEXT["switch_24_button"], command=lambda: self._apply_mask("255.255.255.0"), style="Accent.TButton").grid(row=0, column=3, sticky="ew", padx=6)
        ttk.Button(actions, text=GUI_TEXT["enable_dhcp_button"], command=self._enable_dhcp, style="Secondary.TButton").grid(row=0, column=4, sticky="ew", padx=(6, 0))

    def _on_select(self, _event: Optional[tk.Event] = None) -> None:
        selection = self.tree.selection()
        if not selection:
            self._reset_selection_details()
            return

        values = [str(value) for value in self.tree.item(selection[0])["values"]]
        name, alias, ip, mask, mac, status = values

        self.summary_var.set(format_interface_summary(name, alias, ip, mask, mac, status))
        for key, value in zip(("name", "alias", "ip", "mask", "mac", "status"), values):
            self.detail_vars[key].set(value or "-")

        self._replace_entry(self.entry_ip, "" if ip == "-" else ip)
        self._replace_entry(self.entry_mask, "255.255.255.0" if mask == "-" else mask)

    def refresh_interfaces(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.status_var.set(GUI_TEXT["loading_interfaces"])
        self.root.update_idletasks()

        try:
            interfaces = list_interfaces()
            for index, iface in enumerate(interfaces):
                tag = "even" if index % 2 == 0 else "odd"
                self.tree.insert(
                    "",
                    tk.END,
                    values=(iface.name, iface.alias, iface.ip or "-", iface.mask or "-", iface.mac or "-", iface.status or "-"),
                    tags=(tag,),
                )
            self.status_var.set(GUI_TEXT["loaded_interfaces"].format(count=len(interfaces)))
            if not interfaces:
                self._reset_selection_details()
        except Exception as e:
            messagebox.showerror(GUI_TEXT["error_title"], GUI_TEXT["list_failed"].format(error=e))
            self.status_var.set(GUI_TEXT["list_failed_status"])

    def _reset_selection_details(self) -> None:
        self.summary_var.set(GUI_TEXT["no_interface_selected"])
        for value in self.detail_vars.values():
            value.set("-")

    def _replace_entry(self, entry: ttk.Entry, value: str) -> None:
        entry.delete(0, tk.END)
        entry.insert(0, value)

    def _get_selected_name(self) -> str:
        selection = self.tree.selection()
        if not selection:
            raise ValueError(GUI_TEXT["select_required"])
        item = self.tree.item(selection[0])
        return str(item["values"][0])

    def _current_selected_ip(self) -> str:
        selection = self.tree.selection()
        if not selection:
            return ""
        current_ip = str(self.tree.item(selection[0])["values"][2])
        return "" if current_ip == "-" else current_ip

    def _set_static(self) -> None:
        try:
            name = self._get_selected_name()
        except ValueError as e:
            messagebox.showwarning(GUI_TEXT["warning_title"], str(e))
            return

        ip = self.entry_ip.get().strip()
        mask = self.entry_mask.get().strip()
        gateway = self.entry_gateway.get().strip() or None

        if not ip or not mask:
            messagebox.showwarning(GUI_TEXT["warning_title"], GUI_TEXT["ip_mask_required"])
            return

        self.status_var.set(GUI_TEXT["setting_static"].format(name=name))
        self.root.update_idletasks()

        try:
            set_static(name, ip, mask, gateway)
            messagebox.showinfo(GUI_TEXT["success_title"], GUI_TEXT["static_success"].format(name=name, ip=ip, mask=mask))
            self.refresh_interfaces()
        except PermissionError:
            messagebox.showerror(GUI_TEXT["permission_title"], GUI_TEXT["permission_required"])
            self.status_var.set(GUI_TEXT["permission_status"])
        except Exception as e:
            messagebox.showerror(GUI_TEXT["error_title"], GUI_TEXT["set_static_failed"].format(error=e))
            self.status_var.set(GUI_TEXT["operation_failed_status"])

    def _apply_mask(self, mask: str) -> None:
        try:
            name = self._get_selected_name()
        except ValueError as e:
            messagebox.showwarning(GUI_TEXT["warning_title"], str(e))
            return

        ip = self.entry_ip.get().strip() or self._current_selected_ip()
        if not ip:
            messagebox.showwarning(GUI_TEXT["warning_title"], GUI_TEXT["ip_required"])
            return

        gateway = self.entry_gateway.get().strip() or None

        self.status_var.set(GUI_TEXT["switching_mask"].format(name=name, mask=mask))
        self.root.update_idletasks()

        try:
            set_static(name, ip, mask, gateway)
            messagebox.showinfo(GUI_TEXT["success_title"], GUI_TEXT["mask_success"].format(name=name, ip=ip, mask=mask))
            self.refresh_interfaces()
        except PermissionError:
            messagebox.showerror(GUI_TEXT["permission_title"], GUI_TEXT["permission_required"])
            self.status_var.set(GUI_TEXT["permission_status"])
        except Exception as e:
            messagebox.showerror(GUI_TEXT["error_title"], GUI_TEXT["mask_failed"].format(error=e))
            self.status_var.set(GUI_TEXT["operation_failed_status"])

    def _enable_dhcp(self) -> None:
        try:
            name = self._get_selected_name()
        except ValueError as e:
            messagebox.showwarning(GUI_TEXT["warning_title"], str(e))
            return

        self.status_var.set(GUI_TEXT["enabling_dhcp"].format(name=name))
        self.root.update_idletasks()

        try:
            set_dhcp(name)
            messagebox.showinfo(GUI_TEXT["success_title"], GUI_TEXT["dhcp_success"].format(name=name))
            self.refresh_interfaces()
        except PermissionError:
            messagebox.showerror(GUI_TEXT["permission_title"], GUI_TEXT["permission_required"])
            self.status_var.set(GUI_TEXT["permission_status"])
        except Exception as e:
            messagebox.showerror(GUI_TEXT["error_title"], GUI_TEXT["dhcp_failed"].format(error=e))
            self.status_var.set(GUI_TEXT["operation_failed_status"])


def main() -> int:
    root = tk.Tk()
    NetworkSwitcherGUI(root)
    root.mainloop()
    return 0
