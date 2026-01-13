"""
Tests confirmation of action that uses django-object-action
"""

import tempfile
from csv import DictWriter
from importlib import reload

from selenium.webdriver.common.by import By
from selenium.webdriver.remote.file_detector import LocalFileDetector

from admin_action_tools.constants import BACK, CANCEL, CONFIRM_ACTION, CONFIRM_FORM
from admin_action_tools.tests.helpers import AdminConfirmIntegrationTestCase
from tests.factories import InventoryFactory, ShopFactory
from tests.market.admin import shoppingmall_admin
from tests.market.form import FileActionForm, NoteActionForm

CONFIRM_FORM_UNIQUE = f"{CONFIRM_FORM}_{NoteActionForm.__name__}"
CONFIRM_FORM_FILE = f"{CONFIRM_FORM}_{FileActionForm.__name__}"


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
        self.assertIn(CONFIRM_FORM_UNIQUE, self.selenium.page_source)

        elems = self.selenium.find_elements(By.CLASS_NAME, "datetimeshortcuts")
        for elem in elems:
            elem.find_element(By.TAG_NAME, "a").click()

        self.selenium.find_element(By.ID, "id_note").send_keys("aaaaaa")

        self.selenium.find_element(By.NAME, CONFIRM_FORM_UNIQUE).click()
        inv1.refresh_from_db()
        self.assertTrue("aaaaaa" in inv1.notes)

    def test_change_form_and_confirm(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(
            self.live_server_url + f"/admin/market/inventory/{inv1.id}/actions/add_notes_with_confirmation"
        )
        # Should ask for confirmation of action
        self.assertIn(CONFIRM_FORM_UNIQUE, self.selenium.page_source)

        elems = self.selenium.find_elements(By.CLASS_NAME, "datetimeshortcuts")
        for elem in elems:
            elem.find_element(By.TAG_NAME, "a").click()

        self.selenium.find_element(By.ID, "id_note").send_keys("aaaaaa")

        self.selenium.find_element(By.NAME, CONFIRM_FORM_UNIQUE).click()

        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)

        self.assertIn("aaaaaa", self.selenium.page_source)

        self.selenium.find_element(By.NAME, CONFIRM_ACTION).click()

        inv1.refresh_from_db()
        self.assertIn("aaaaaa", inv1.notes)

    def test_change_form_and_confirm_form_back(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(
            self.live_server_url + f"/admin/market/inventory/{inv1.id}/actions/add_notes_with_confirmation"
        )

        self.selenium.find_element(By.CLASS_NAME, "cancel-link-nojs").click()
        self.assertTrue(self.selenium.current_url.endswith(f"/admin/market/inventory/{inv1.id}/change/"))

    def test_change_form_and_confirm_confirm_back(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(
            self.live_server_url + f"/admin/market/inventory/{inv1.id}/actions/add_notes_with_confirmation"
        )

        # Should ask for confirmation form
        self.assertIn(CONFIRM_FORM_UNIQUE, self.selenium.page_source)

        elems = self.selenium.find_elements(By.CLASS_NAME, "datetimeshortcuts")
        for elem in elems:
            elem.find_element(By.TAG_NAME, "a").click()

        self.selenium.find_element(By.ID, "id_note").send_keys("aaaaaa")

        self.selenium.find_element(By.NAME, CONFIRM_FORM_UNIQUE).click()

        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)
        self.selenium.find_element(By.NAME, BACK).click()

        # Should ask for confirmation form
        self.assertIn(CONFIRM_FORM_UNIQUE, self.selenium.page_source)

        # back again
        self.selenium.find_element(By.CLASS_NAME, "cancel-link-nojs").click()
        self.assertTrue(self.selenium.current_url.endswith(f"/admin/market/inventory/{inv1.id}/change/"))

    def test_change_form_and_confirm_cancel(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(
            self.live_server_url + f"/admin/market/inventory/{inv1.id}/actions/add_notes_with_confirmation"
        )

        # Should ask for confirmation form
        self.assertIn(CONFIRM_FORM_UNIQUE, self.selenium.page_source)

        elems = self.selenium.find_elements(By.CLASS_NAME, "datetimeshortcuts")
        for elem in elems:
            elem.find_element(By.TAG_NAME, "a").click()

        self.selenium.find_element(By.ID, "id_note").send_keys("aaaaaa")

        self.selenium.find_element(By.NAME, CONFIRM_FORM_UNIQUE).click()

        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)
        self.selenium.find_element(By.NAME, CANCEL).click()

        self.assertTrue(self.selenium.current_url.endswith(f"/admin/market/inventory/{inv1.id}/change/"))

    def test_form_with_file_action(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(self.live_server_url + "/admin/market/inventory/actions/add_stock")

        with tempfile.NamedTemporaryFile("w", delete=False) as fp:
            writer = DictWriter(fp, fieldnames=["id", "qt"], delimiter=";")
            writer.writeheader()
            writer.writerow({"id": inv1.id, "qt": 230})
            fp.close()

            file_input = self.selenium.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(fp.name)

            self.selenium.find_element(By.NAME, CONFIRM_FORM_FILE).click()

        inv1.refresh_from_db()
        self.assertEqual(inv1.quantity, 230)

    def test_form_with_file_and_confirm_action(self):
        shop = ShopFactory()
        inv1 = InventoryFactory(shop=shop, quantity=10)

        self.selenium.get(self.live_server_url + "/admin/market/inventory/actions/add_stock_with_confirm")

        with tempfile.NamedTemporaryFile("w", delete=False) as fp:
            writer = DictWriter(fp, fieldnames=["id", "qt"], delimiter=";")
            writer.writeheader()
            writer.writerow({"id": inv1.id, "qt": 230})
            fp.close()

            file_input = self.selenium.find_element(By.CSS_SELECTOR, "input[type='file']")
            file_input.send_keys(fp.name)

            self.selenium.find_element(By.NAME, CONFIRM_FORM_FILE).click()

        # Should ask for confirmation of action
        self.assertIn(CONFIRM_ACTION, self.selenium.page_source)

        self.assertIn(fp.name.split("/")[-1], self.selenium.page_source)

        self.selenium.find_element(By.NAME, CONFIRM_ACTION).click()

        inv1.refresh_from_db()
        self.assertEqual(inv1.quantity, 230)
