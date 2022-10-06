from django.contrib.admin import ModelAdmin

from admin_action_tools.admin import AdminConfirmMixin


class ItemSaleAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
