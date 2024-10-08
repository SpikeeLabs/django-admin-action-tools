from unittest import mock

from django.core.cache import cache

from admin_action_tools.constants import CACHE_KEYS
from admin_action_tools.tests.helpers import AdminConfirmTestCase
from tests.factories import ShopFactory
from tests.market.admin import ShoppingMallAdmin
from tests.market.models import GeneralManager, ShoppingMall, Town


@mock.patch.object(ShoppingMallAdmin, "inlines", [])
class TestAdminOptions(AdminConfirmTestCase):
    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "fields", ["name", "town"])
    def test_change_model_with_m2m_field_without_input_for_m2m_field_should_work(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(f"/admin/market/shoppingmall/{mall.id}/change/", data=data)

        # Should be shown confirmation page
        self._assertSubmitHtml(rendered_content=response.rendered_content, save_action="_continue")

        # Should not have cached the unsaved obj
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNone(cached_item)

        # Should not have saved changes yet
        self.assertEqual(ShoppingMall.objects.count(), 1)
        mall.refresh_from_db()
        self.assertEqual(mall.name, "mall")
        self.assertEqual(mall.general_manager, gm)
        self.assertEqual(mall.town, town)
        for shop in mall.shops.all():
            self.assertIn(shop, shops)

        # Click "Yes, I'm Sure"
        confirmation_received_data = data
        del confirmation_received_data["_confirm_change"]

        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/",
            data=confirmation_received_data,
        )

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should have saved obj
        self.assertEqual(ShoppingMall.objects.count(), 1)
        saved_item = ShoppingMall.objects.all().first()
        # should have updated fields that were in form
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.town, town2)
        # should have presevered the fields that are not in form
        self.assertEqual(saved_item.general_manager, gm)
        for shop in saved_item.shops.all():
            self.assertIn(shop, shops)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "exclude", ["shops"])
    def test_when_m2m_field_in_exclude_changes_to_field_should_not_be_saved(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "general_manager": gm2.id,
            "shops": [1],
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(f"/admin/market/shoppingmall/{mall.id}/change/", data=data)
        # Should be shown confirmation page
        self._assertSubmitHtml(rendered_content=response.rendered_content, save_action="_continue")

        # Should not have cached the unsaved obj
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNone(cached_item)

        # Should not have saved changes yet
        self.assertEqual(ShoppingMall.objects.count(), 1)
        mall.refresh_from_db()
        self.assertEqual(mall.name, "mall")
        self.assertEqual(mall.general_manager, gm)
        self.assertEqual(mall.town, town)
        for shop in mall.shops.all():
            self.assertIn(shop, shops)

        # Click "Yes, I'm Sure"
        confirmation_received_data = data
        del confirmation_received_data["_confirm_change"]

        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/",
            data=confirmation_received_data,
        )

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should have saved obj
        self.assertEqual(ShoppingMall.objects.count(), 1)
        saved_item = ShoppingMall.objects.all().first()
        # should have updated fields that were in form
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.town, town2)
        self.assertEqual(saved_item.general_manager, gm2)
        # should have presevered the fields that are not in form (exclude)
        for shop in saved_item.shops.all():
            self.assertIn(shop, shops)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))

    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "exclude", ["shops", "name"])
    @mock.patch.object(ShoppingMallAdmin, "inlines", [])
    def test_if_confirmation_fields_in_exclude_should_not_trigger_confirmation(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "general_manager": gm2.id,
            "shops": [1],
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(f"/admin/market/shoppingmall/{mall.id}/change/", data=data)
        # Should not be shown confirmation page
        # SInce we used "Save and Continue", should show change page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should have saved the non excluded fields
        mall.refresh_from_db()
        for shop in shops:
            self.assertIn(shop, mall.shops.all())
        self.assertEqual(mall.name, "mall")
        # Should have saved other fields
        self.assertEqual(mall.town, town2)
        self.assertEqual(mall.general_manager, gm2)

    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "readonly_fields", ["shops", "name"])
    @mock.patch.object(ShoppingMallAdmin, "inlines", [])
    def test_if_confirmation_fields_in_readonly_should_not_trigger_confirmation(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "general_manager": gm2.id,
            "shops": [1],
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(f"/admin/market/shoppingmall/{mall.id}/change/", data=data)
        # Should not be shown confirmation page
        # SInce we used "Save and Continue", should show change page
        self.assertEqual(response.status_code, 302)
        self.assertEqual(response.url, f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should have saved the non excluded fields
        mall.refresh_from_db()
        for shop in shops:
            self.assertIn(shop, mall.shops.all())
        self.assertEqual(mall.name, "mall")
        # Should have saved other fields
        self.assertEqual(mall.town, town2)
        self.assertEqual(mall.general_manager, gm2)

    @mock.patch.object(ShoppingMallAdmin, "confirmation_fields", ["name"])
    @mock.patch.object(ShoppingMallAdmin, "readonly_fields", ["shops"])
    @mock.patch.object(ShoppingMallAdmin, "inlines", [])
    def test_readonly_fields_should_not_change(self):
        gm = GeneralManager.objects.create(name="gm")
        shops = [ShopFactory() for i in range(3)]
        town = Town.objects.create(name="town")
        mall = ShoppingMall.objects.create(name="mall", general_manager=gm, town=town)
        mall.shops.set(shops)

        # new values
        gm2 = GeneralManager.objects.create(name="gm2")
        town2 = Town.objects.create(name="town2")

        data = {
            "id": mall.id,
            "name": "name",
            "general_manager": gm2.id,
            "shops": [1],
            "town": town2.id,
            "_confirm_change": True,
            "_continue": True,
        }
        response = self.client.post(f"/admin/market/shoppingmall/{mall.id}/change/", data=data)
        # Should be shown confirmation page
        self._assertSubmitHtml(rendered_content=response.rendered_content, save_action="_continue")

        # Should not have cached the unsaved obj
        cached_item = cache.get(CACHE_KEYS["object"])
        self.assertIsNone(cached_item)

        # Should not have saved changes yet
        self.assertEqual(ShoppingMall.objects.count(), 1)
        mall.refresh_from_db()
        self.assertEqual(mall.name, "mall")
        self.assertEqual(mall.general_manager, gm)
        self.assertEqual(mall.town, town)
        for shop in mall.shops.all():
            self.assertIn(shop, shops)

        # Click "Yes, I'm Sure"
        confirmation_received_data = data
        del confirmation_received_data["_confirm_change"]

        response = self.client.post(
            f"/admin/market/shoppingmall/{mall.id}/change/",
            data=confirmation_received_data,
        )

        # Should not have redirected to changelist
        self.assertEqual(response.url, f"/admin/market/shoppingmall/{mall.id}/change/")

        # Should have saved obj
        self.assertEqual(ShoppingMall.objects.count(), 1)
        saved_item = ShoppingMall.objects.all().first()
        # should have updated fields that were in form
        self.assertEqual(saved_item.name, data["name"])
        self.assertEqual(saved_item.town, town2)
        self.assertEqual(saved_item.general_manager, gm2)
        # should have presevered the fields that are not in form (exclude)
        for shop in saved_item.shops.all():
            self.assertIn(shop, shops)

        # Should have cleared cache
        for key in CACHE_KEYS.values():
            self.assertIsNone(cache.get(key))
