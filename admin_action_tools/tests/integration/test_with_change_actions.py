"""
Tests confirmation of action that uses django-object-action
"""
from importlib import reload

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import LocalFileDetector

from admin_action_tools.constants import CONFIRM_ACTION
from admin_action_tools.tests.helpers import AdminConfirmIntegrationTestCase
from tests.factories import InventoryFactory, ShopFactory
from tests.market.admin import shoppingmall_admin


class ConfirmWithChangeActionTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.selenium.file_detector = LocalFileDetector()
        super().setUp()

    def tearDown(self):
        reload(shoppingmall_admin)
        super().tearDown()

    def test_change_and_changelist_action(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)
        inv2 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(self.live_server_url + f"/admin/market/inventory/{inv1.id}/actions/quantity_up")
        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)

        self.selenium.find_element(By.NAME, CONFIRM_ACTION).click()
        inv1.refresh_from_db()
        self.assertEqual(inv1.quantity, 11)

        self.selenium.get(self.live_server_url + f"/admin/market/inventory/{inv2.id}/actions/quantity_up")
        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)

        self.selenium.find_element(By.NAME, CONFIRM_ACTION).click()
        inv2.refresh_from_db()
        self.assertEqual(inv2.quantity, 11)

        self.selenium.get(self.live_server_url + "/admin/market/inventory/actions/quantity_down/")
        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)
        self.selenium.find_element(By.NAME, CONFIRM_ACTION).click()

        inv1.refresh_from_db()
        inv2.refresh_from_db()
        self.assertEqual(inv1.quantity, 0)
        self.assertEqual(inv2.quantity, 0)
