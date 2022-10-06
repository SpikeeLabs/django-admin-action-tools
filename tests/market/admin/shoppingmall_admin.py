from django.contrib.admin import ModelAdmin
from django.contrib.admin.options import StackedInline

from admin_action_tools.admin import AdminConfirmMixin
from tests.market.models import ShoppingMall


class ShopInline(StackedInline):
    model = ShoppingMall.shops.through


class ShoppingMallAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
    confirmation_fields = ["name"]

    inlines = [ShopInline]
    raw_id_fields = ["general_manager"]
