import unittest

from network_switcher.gui_helpers import GATEWAY_HELP_TEXT, format_interface_summary


class GUIHelperTests(unittest.TestCase):
    def test_gateway_hint_explains_preserved_gateway_behavior(self) -> None:
        self.assertIn("preserve", GATEWAY_HELP_TEXT.lower())
        self.assertIn("current gateway", GATEWAY_HELP_TEXT.lower())

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
