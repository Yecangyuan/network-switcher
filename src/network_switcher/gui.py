"""Tkinter GUI for the network switcher."""

import tkinter as tk
from tkinter import ttk, messagebox
from typing import Optional

from .core import list_interfaces, set_static, set_dhcp


class NetworkSwitcherGUI:
    """Cross-platform GUI for switching ethernet subnet masks."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.root.title("Network Switcher")
        self.root.geometry("900x600")
        self.root.minsize(700, 450)

        self._build_ui()
        self.refresh_interfaces()

    def _build_ui(self) -> None:
        # Top frame: interface list
        list_frame = ttk.LabelFrame(self.root, text="Network Interfaces", padding=(10, 5))
        list_frame.pack(fill=tk.BOTH, expand=True, padx=10, pady=(10, 5))

        columns = ("name", "alias", "ip", "mask", "mac", "status")
        self.tree = ttk.Treeview(
            list_frame,
            columns=columns,
            show="headings",
            selectmode="browse",
        )
        self.tree.heading("name", text="Name")
        self.tree.heading("alias", text="Alias")
        self.tree.heading("ip", text="IP Address")
        self.tree.heading("mask", text="Subnet Mask")
        self.tree.heading("mac", text="MAC Address")
        self.tree.heading("status", text="Status")

        self.tree.column("name", width=120, minwidth=80)
        self.tree.column("alias", width=140, minwidth=80)
        self.tree.column("ip", width=120, minwidth=80)
        self.tree.column("mask", width=120, minwidth=80)
        self.tree.column("mac", width=150, minwidth=80)
        self.tree.column("status", width=80, minwidth=60)

        vsb = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.tree.yview)
        hsb = ttk.Scrollbar(list_frame, orient=tk.HORIZONTAL, command=self.tree.xview)
        self.tree.configure(yscrollcommand=vsb.set, xscrollcommand=hsb.set)

        self.tree.grid(row=0, column=0, sticky="nsew")
        vsb.grid(row=0, column=1, sticky="ns")
        hsb.grid(row=1, column=0, sticky="ew")
        list_frame.grid_rowconfigure(0, weight=1)
        list_frame.grid_columnconfigure(0, weight=1)

        self.tree.bind("<<TreeviewSelect>>", self._on_select)

        # Middle frame: selected interface info
        info_frame = ttk.LabelFrame(self.root, text="Selected Interface", padding=(10, 5))
        info_frame.pack(fill=tk.X, padx=10, pady=5)

        self.lbl_info = ttk.Label(info_frame, text="No interface selected.")
        self.lbl_info.pack(anchor=tk.W)

        # Bottom frame: configuration
        config_frame = ttk.LabelFrame(self.root, text="Configuration", padding=(10, 5))
        config_frame.pack(fill=tk.X, padx=10, pady=5)

        ttk.Label(config_frame, text="IP Address:").grid(row=0, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_ip = ttk.Entry(config_frame, width=20)
        self.entry_ip.grid(row=0, column=1, sticky=tk.W, padx=5, pady=5)

        ttk.Label(config_frame, text="Subnet Mask:").grid(row=0, column=2, sticky=tk.W, padx=5, pady=5)
        self.entry_mask = ttk.Entry(config_frame, width=20)
        self.entry_mask.insert(0, "255.255.255.0")
        self.entry_mask.grid(row=0, column=3, sticky=tk.W, padx=5, pady=5)

        ttk.Label(config_frame, text="Gateway:").grid(row=1, column=0, sticky=tk.W, padx=5, pady=5)
        self.entry_gateway = ttk.Entry(config_frame, width=20)
        self.entry_gateway.grid(row=1, column=1, sticky=tk.W, padx=5, pady=5)

        # Buttons
        btn_frame = ttk.Frame(self.root, padding=(10, 5))
        btn_frame.pack(fill=tk.X, padx=10, pady=(5, 10))

        ttk.Button(btn_frame, text="Refresh", command=self.refresh_interfaces).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Set Static IP", command=self._set_static).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Enable DHCP", command=self._enable_dhcp).pack(side=tk.LEFT, padx=5)

        ttk.Separator(btn_frame, orient=tk.VERTICAL).pack(side=tk.LEFT, fill=tk.Y, padx=10)

        ttk.Button(btn_frame, text="Switch to /16 (255.255.0.0)", command=lambda: self._apply_mask("255.255.0.0")).pack(side=tk.LEFT, padx=5)
        ttk.Button(btn_frame, text="Switch to /24 (255.255.255.0)", command=lambda: self._apply_mask("255.255.255.0")).pack(side=tk.LEFT, padx=5)

        # Status bar
        self.status_var = tk.StringVar(value="Ready")
        status_bar = ttk.Label(self.root, textvariable=self.status_var, relief=tk.SUNKEN, anchor=tk.W)
        status_bar.pack(fill=tk.X, side=tk.BOTTOM)

    def _on_select(self, _event: Optional[tk.Event] = None) -> None:
        selection = self.tree.selection()
        if not selection:
            self.lbl_info.config(text="No interface selected.")
            return

        item = self.tree.item(selection[0])
        values = item["values"]
        name, alias, ip, mask, mac, status = values
        self.lbl_info.config(
            text=f"Name: {name}  |  Alias: {alias}  |  Current IP: {ip or '-'}  |  Mask: {mask or '-'}  |  MAC: {mac or '-'}  |  Status: {status or '-'}"
        )

    def refresh_interfaces(self) -> None:
        self.tree.delete(*self.tree.get_children())
        self.status_var.set("Loading interfaces...")
        self.root.update_idletasks()

        try:
            interfaces = list_interfaces()
            for iface in interfaces:
                self.tree.insert(
                    "",
                    tk.END,
                    values=(iface.name, iface.alias, iface.ip or "-", iface.mask or "-", iface.mac or "-", iface.status or "-"),
                )
            self.status_var.set(f"Loaded {len(interfaces)} interface(s)")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to list interfaces:\n{e}")
            self.status_var.set("Error loading interfaces")

    def _get_selected_name(self) -> str:
        selection = self.tree.selection()
        if not selection:
            raise ValueError("No interface selected.")
        item = self.tree.item(selection[0])
        return str(item["values"][0])

    def _set_static(self) -> None:
        try:
            name = self._get_selected_name()
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))
            return

        ip = self.entry_ip.get().strip()
        mask = self.entry_mask.get().strip()
        gateway = self.entry_gateway.get().strip() or None

        if not ip or not mask:
            messagebox.showwarning("Warning", "IP Address and Subnet Mask are required.")
            return

        self.status_var.set(f"Setting static IP for {name}...")
        self.root.update_idletasks()

        try:
            set_static(name, ip, mask, gateway)
            messagebox.showinfo("Success", f"Static IP set for {name}:\n{ip} / {mask}")
            self.refresh_interfaces()
        except PermissionError:
            messagebox.showerror("Permission Denied", "Administrator/root privileges are required to modify network settings.")
            self.status_var.set("Permission denied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to set static IP:\n{e}")
            self.status_var.set("Error")

    def _apply_mask(self, mask: str) -> None:
        try:
            name = self._get_selected_name()
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))
            return

        ip = self.entry_ip.get().strip()
        if not ip:
            # Fallback to current interface IP
            selection = self.tree.selection()
            if selection:
                current_ip = self.tree.item(selection[0])["values"][2]
                if current_ip and current_ip != "-":
                    ip = current_ip

        if not ip:
            messagebox.showwarning("Warning", "IP Address is required. Enter an IP or select an interface that already has one.")
            return

        gateway = self.entry_gateway.get().strip() or None

        self.status_var.set(f"Switching {name} to {mask}...")
        self.root.update_idletasks()

        try:
            set_static(name, ip, mask, gateway)
            messagebox.showinfo("Success", f"Subnet mask changed for {name}:\n{ip} / {mask}")
            self.refresh_interfaces()
        except PermissionError:
            messagebox.showerror("Permission Denied", "Administrator/root privileges are required to modify network settings.")
            self.status_var.set("Permission denied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to change subnet mask:\n{e}")
            self.status_var.set("Error")

    def _enable_dhcp(self) -> None:
        try:
            name = self._get_selected_name()
        except ValueError as e:
            messagebox.showwarning("Warning", str(e))
            return

        self.status_var.set(f"Enabling DHCP for {name}...")
        self.root.update_idletasks()

        try:
            set_dhcp(name)
            messagebox.showinfo("Success", f"DHCP enabled for {name}.")
            self.refresh_interfaces()
        except PermissionError:
            messagebox.showerror("Permission Denied", "Administrator/root privileges are required to modify network settings.")
            self.status_var.set("Permission denied")
        except Exception as e:
            messagebox.showerror("Error", f"Failed to enable DHCP:\n{e}")
            self.status_var.set("Error")


def main() -> int:
    root = tk.Tk()
    NetworkSwitcherGUI(root)
    root.mainloop()
    return 0
