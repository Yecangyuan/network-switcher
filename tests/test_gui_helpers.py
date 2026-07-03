import unittest

from network_switcher.gui_helpers import GATEWAY_HELP_TEXT, GUI_TEXT, format_interface_summary


class GUIHelperTests(unittest.TestCase):
    def test_gateway_hint_explains_preserved_gateway_behavior(self) -> None:
        self.assertIn("留空", GATEWAY_HELP_TEXT)
        self.assertIn("当前网关", GATEWAY_HELP_TEXT)

    def test_primary_gui_text_is_chinese(self) -> None:
        self.assertEqual(GUI_TEXT["window_title"], "网络切换器")
        self.assertEqual(GUI_TEXT["interfaces_title"], "网络接口")
        self.assertEqual(GUI_TEXT["selected_title"], "已选接口")
        self.assertEqual(GUI_TEXT["configuration_title"], "网络配置")
        self.assertEqual(GUI_TEXT["refresh_button"], "刷新")
        self.assertEqual(GUI_TEXT["set_static_button"], "设置静态 IP")
        self.assertEqual(GUI_TEXT["enable_dhcp_button"], "启用 DHCP")

    def test_format_interface_summary_compacts_selected_interface_details(self) -> None:
        summary = format_interface_summary(
            name="en7",
            alias="USB LAN",
            ip="192.168.1.30",
            mask="255.255.255.0",
            mac="aa:bb:cc:dd:ee:ff",
            status="Up",
        )

        self.assertEqual(
            summary,
            "en7 | USB LAN | 192.168.1.30 | 255.255.255.0 | aa:bb:cc:dd:ee:ff | Up",
        )


if __name__ == "__main__":
    unittest.main()
