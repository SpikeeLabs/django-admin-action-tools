"""
Tests confirmation of action that uses django-object-action
"""
from importlib import reload

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import LocalFileDetector

from admin_action_tools.constants import BACK, CANCEL, CONFIRM_ACTION, CONFIRM_FORM
from admin_action_tools.tests.helpers import AdminConfirmIntegrationTestCase
from tests.factories import InventoryFactory, ShopFactory
from tests.market.admin import shoppingmall_admin
from tests.market.form import NoteActionForm, NoteClearForm

CONFIRM_FORM_UNIQUE = f"{CONFIRM_FORM}_{NoteActionForm.__name__}"
CONFIRM_FORM_UNIQUE_2 = f"{CONFIRM_FORM}_{NoteClearForm.__name__}"


class MultipleFormActionTests(AdminConfirmIntegrationTestCase):
    def setUp(self):
        self.selenium.file_detector = LocalFileDetector()
        super().setUp()

    def tearDown(self):
        reload(shoppingmall_admin)
        super().tearDown()

    def test_change_form_and_confirm(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(self.live_server_url + f"/admin/market/inventory/{inv1.id}/actions/add_notes_with_clear")
        # Should ask for confirmation of action
        self.assertIn(CONFIRM_FORM_UNIQUE, self.selenium.page_source)

        elems = self.selenium.find_elements(By.CLASS_NAME, "datetimeshortcuts")
        for elem in elems:
            elem.find_element(By.TAG_NAME, "a").click()

        self.selenium.find_element(By.ID, "id_note").send_keys("aaaaaa")

        self.selenium.find_element(By.NAME, CONFIRM_FORM_UNIQUE).click()

        # second form
        self.assertIn(CONFIRM_FORM_UNIQUE_2, self.selenium.page_source)
        self.selenium.find_element(By.ID, "id_clear_notes").click()
        self.selenium.find_element(By.NAME, CONFIRM_FORM_UNIQUE_2).click()

        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)

        self.assertIn("aaaaaa", self.selenium.page_source)

        self.selenium.find_element(By.NAME, CONFIRM_ACTION).click()

        inv1.refresh_from_db()
        self.assertIn("aaaaaa", inv1.notes)

    def test_change_form_and_confirm_confirm_back(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(self.live_server_url + f"/admin/market/inventory/{inv1.id}/actions/add_notes_with_clear")

        # Should ask for confirmation form
        self.assertIn(CONFIRM_FORM_UNIQUE, self.selenium.page_source)

        elems = self.selenium.find_elements(By.CLASS_NAME, "datetimeshortcuts")
        for elem in elems:
            elem.find_element(By.TAG_NAME, "a").click()

        self.selenium.find_element(By.ID, "id_note").send_keys("aaaaaa")

        self.selenium.find_element(By.NAME, CONFIRM_FORM_UNIQUE).click()

        # second form
        self.assertIn(CONFIRM_FORM_UNIQUE_2, self.selenium.page_source)
        self.selenium.find_element(By.ID, "id_clear_notes").click()
        self.selenium.find_element(By.NAME, CONFIRM_FORM_UNIQUE_2).click()

        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)
        self.selenium.find_element(By.NAME, BACK).click()

        # Should ask for confirmation form
        self.assertIn(CONFIRM_FORM_UNIQUE_2, self.selenium.page_source)

        self.selenium.find_element(By.NAME, BACK).click()

        # Should ask for confirmation form
        self.assertIn(CONFIRM_FORM_UNIQUE, self.selenium.page_source)

        # back again
        self.selenium.find_element(By.CLASS_NAME, "cancel-link-nojs").click()
        self.assertTrue(self.selenium.current_url.endswith(f"/admin/market/inventory/{inv1.id}/change/"))
