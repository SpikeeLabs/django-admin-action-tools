from django.contrib.admin import ModelAdmin
from django_object_actions import DjangoObjectActions

from admin_action_tools.admin import (
    ActionFormMixin,
    AdminConfirmMixin,
    add_form_to_action,
    confirm_action,
)
from tests.market.form import NoteActionForm


class InventoryAdmin(AdminConfirmMixin, ActionFormMixin, DjangoObjectActions, ModelAdmin):
    list_display = ("shop", "item", "quantity")

    confirm_change = True
    confirm_add = True
    confirmation_fields = ["quantity"]

    change_actions = ["quantity_up", "add_notes", "add_notes_with_confirmation"]
    changelist_actions = ["quantity_down"]

    @confirm_action
    def quantity_up(self, request, obj):
        obj.quantity = obj.quantity + 1
        obj.save()

    @confirm_action
    def quantity_down(self, request, queryset):
        queryset.update(quantity=0)

    @add_form_to_action(NoteActionForm)
    def add_notes(self, request, object, form=None):
        object.notes += f"\n\n{form.cleaned_data['date']}\n{form.cleaned_data['note']}"
        object.save()

    @add_form_to_action(NoteActionForm)
    @confirm_action
    def add_notes_with_confirmation(self, request, object, form=None):
        object.notes += f"\n\n{form.cleaned_data['date']}\n{form.cleaned_data['note']}"
        object.save()
