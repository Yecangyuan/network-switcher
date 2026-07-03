"""Small GUI helpers that do not depend on Tk."""

GUI_TEXT = {
    "window_title": "网络切换器",
    "ready": "就绪",
    "no_interface_selected": "未选择网卡",
    "header_title": "网络切换器",
    "header_subtitle": "快速查看网卡、切换子网掩码，并在未填写网关时默认保留当前网关。",
    "interfaces_title": "网络接口",
    "selected_title": "已选接口",
    "configuration_title": "网络配置",
    "device_column": "设备名",
    "service_column": "服务名称",
    "ip_column": "IP 地址",
    "mask_column": "子网掩码",
    "mac_column": "MAC 地址",
    "status_column": "状态",
    "device_label": "设备名",
    "service_label": "服务名称",
    "ip_label": "IP 地址",
    "mask_label": "子网掩码",
    "mac_label": "MAC 地址",
    "status_label": "状态",
    "ip_required_label": "IP 地址（必填）",
    "mask_required_label": "子网掩码（必填）",
    "gateway_label": "网关",
    "gateway_help": "留空时会尽量保留当前网关。",
    "refresh_button": "刷新",
    "set_static_button": "设置静态 IP",
    "switch_16_button": "切换到 /16",
    "switch_24_button": "切换到 /24",
    "enable_dhcp_button": "启用 DHCP",
    "loading_interfaces": "正在加载网络接口...",
    "loaded_interfaces": "已加载 {count} 个网络接口",
    "error_title": "错误",
    "warning_title": "提示",
    "success_title": "成功",
    "permission_title": "权限不足",
    "list_failed": "加载网络接口失败：\n{error}",
    "list_failed_status": "加载网络接口失败",
    "select_required": "请先选择一个网络接口。",
    "ip_mask_required": "IP 地址和子网掩码为必填项。",
    "setting_static": "正在为 {name} 设置静态 IP...",
    "static_success": "已为 {name} 设置静态 IP：\n{ip} / {mask}",
    "permission_required": "需要管理员/root 权限才能修改网络设置。",
    "permission_status": "权限不足",
    "operation_failed_status": "操作失败",
    "set_static_failed": "设置静态 IP 失败：\n{error}",
    "ip_required": "请输入 IP 地址，或选择一个已有 IP 的网络接口。",
    "switching_mask": "正在将 {name} 切换到 {mask}...",
    "mask_success": "已为 {name} 修改子网掩码：\n{ip} / {mask}",
    "mask_failed": "修改子网掩码失败：\n{error}",
    "enabling_dhcp": "正在为 {name} 启用 DHCP...",
    "dhcp_success": "已为 {name} 启用 DHCP。",
    "dhcp_failed": "启用 DHCP 失败：\n{error}",
}

GATEWAY_HELP_TEXT = GUI_TEXT["gateway_help"]


def format_interface_summary(name: str, alias: str, ip: str, mask: str, mac: str, status: str) -> str:
    """Return a compact single-line interface summary."""
    values = [name, alias, ip, mask, mac, status]
    return " | ".join(value or "-" for value in values)
