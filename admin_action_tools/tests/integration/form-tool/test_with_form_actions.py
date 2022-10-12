"""
Tests confirmation of action that uses django-object-action
"""
from importlib import reload

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import LocalFileDetector

from admin_action_tools.constants import CONFIRM_ACTION, CONFIRM_FORM
from admin_action_tools.tests.helpers import AdminConfirmIntegrationTestCase
from tests.factories import InventoryFactory, ShopFactory
from tests.market.admin import shoppingmall_admin


class FormActionTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.selenium.file_detector = LocalFileDetector()
        super().setUp()

    def tearDown(self):
        reload(shoppingmall_admin)
        super().tearDown()

    def test_change_and_changelist_action(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(self.live_server_url + f"/admin/market/inventory/{inv1.id}/actions/add_notes")
        # Should ask for confirmation of action
        self.assertIn(CONFIRM_FORM, self.selenium.page_source)

        elems = self.selenium.find_elements(By.CLASS_NAME, "datetimeshortcuts")
        for elem in elems:
            elem.find_element(By.TAG_NAME, "a").click()

        self.selenium.find_element(By.ID, "id_note").send_keys("aaaaaa")

        self.selenium.find_element(By.NAME, CONFIRM_FORM).click()
        inv1.refresh_from_db()
        self.assertTrue("aaaaaa" in inv1.notes)
