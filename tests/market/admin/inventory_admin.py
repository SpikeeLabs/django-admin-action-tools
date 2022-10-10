from django.contrib.admin import ModelAdmin
from django_object_actions import DjangoObjectActions
from more_itertools import quantify

from admin_action_tools.admin import AdminConfirmMixin, confirm_action


class InventoryAdmin(AdminConfirmMixin, DjangoObjectActions, ModelAdmin):
    list_display = ("shop", "item", "quantity")

    confirm_change = True
    confirm_add = True
    confirmation_fields = ["quantity"]

    change_actions = ["quantity_up"]
    changelist_actions = ["quantity_down"]

    @confirm_action
    def quantity_up(self, request, obj):
        obj.quantity = obj.quantity + 1
        obj.save()

    quantity_up.label = "Quantity++"

    @confirm_action
    def quantity_down(self, request, queryset):
        queryset.update(quantity=0)
