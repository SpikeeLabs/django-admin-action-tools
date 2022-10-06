from django.contrib.admin import ModelAdmin

from admin_action_tools.admin import AdminConfirmMixin


class TransactionAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
