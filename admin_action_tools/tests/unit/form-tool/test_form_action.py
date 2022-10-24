from django.contrib.auth.models import User
from django.urls import reverse

from admin_action_tools.constants import CONFIRM_FORM
from admin_action_tools.tests.helpers import AdminConfirmTestCase
from tests.factories import InventoryFactory, ShopFactory
from tests.market.form import NoteActionForm

CONFIRM_FORM_UNIQUE = f"{CONFIRM_FORM}_{NoteActionForm.__name__}"


class TestFormAction(AdminConfirmTestCase):
    @classmethod
    def setUpTestData(cls):
        cls.superuser = User.objects.create_superuser(  # nosec
            username="super", email="super@email.org", password="pass"
        )

    def setUp(self):
        super().setUp()
        self.shop = ShopFactory()
        self.inv = InventoryFactory(shop=self.shop, quantity=10)

    def test_form_action(self):
        response = self.client.post(
            reverse("admin:market_inventory_actions", kwargs={"pk": self.inv.pk, "tool": "add_notes"}),
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should not use confirmation page, since we clicked Yes, I'm sure
        self.assertEqual(
            response.template_name,
            [
                "admin/market/inventory/form_tool/action_form.html",
                "admin/market/form_tool/action_form.html",
                "admin/form_tool/action_form.html",
            ],
        )

        # The action was to show user a message, and should happen
        self.assertIn("Configure the", response.rendered_content)

    def test_form_action_with_valid_form(self):
        post_params = {CONFIRM_FORM_UNIQUE: ["Continue"], "date_0": "2022-10-11", "date_1": "14:33:21", "note": "Note"}
        response = self.client.post(
            reverse("admin:market_inventory_actions", kwargs={"pk": self.inv.pk, "tool": "add_notes"}),
            data=post_params,
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should not use confirmation page, since we clicked Yes, I'm sure
        self.assertEqual(response.template_name, "django_object_actions/change_form.html")

        self.inv.refresh_from_db()
        self.assertEqual(self.inv.notes, "This is the default\n\n2022-10-11 14:33:21+00:00\nNote")

    def test_form_action_with_not_valid_form(self):
        post_params = {CONFIRM_FORM_UNIQUE: ["Continue"], "date_0": "", "date_1": "", "note": "Note"}
        response = self.client.post(
            reverse("admin:market_inventory_actions", kwargs={"pk": self.inv.pk, "tool": "add_notes"}),
            data=post_params,
            follow=True,  # Follow the redirect to get content
        )
        self.assertIsNotNone(response)
        self.assertEqual(response.status_code, 200)
        # Should not use confirmation page, since we clicked Yes, I'm sure
        self.assertEqual(
            response.template_name,
            [
                "admin/market/inventory/form_tool/action_form.html",
                "admin/market/form_tool/action_form.html",
                "admin/form_tool/action_form.html",
            ],
        )

        self.assertIn("Configure the", response.rendered_content)
        self.assertIn("This field is required.", response.rendered_content)
