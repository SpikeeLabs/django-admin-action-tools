from django.contrib.admin import ModelAdmin
from django_object_actions import DjangoObjectActions

from admin_action_tools.admin import (
    ActionFormMixin,
    AdminConfirmMixin,
    add_form_to_action,
    confirm_action,
)
from tests.market.form import NoteActionForm, NoteClearForm


class InventoryAdmin(AdminConfirmMixin, ActionFormMixin, DjangoObjectActions, ModelAdmin):
    list_display = ("shop", "item", "quantity")

    confirm_change = True
    confirm_add = True
    confirmation_fields = ["quantity"]

    change_actions = ["quantity_up", "add_notes", "add_notes_with_confirmation", "add_notes_with_clear"]
    changelist_actions = ["quantity_down", "add_notes_with_confirmation_many", "add_notes_with_confirmation_no_form"]

    @confirm_action()
    def quantity_up(self, request, obj):
        obj.quantity = obj.quantity + 1
        obj.save()

    @confirm_action()
    def quantity_down(self, request, queryset):
        queryset.update(quantity=0)

    @add_form_to_action(NoteActionForm)
    def add_notes(self, request, object, form=None):
        object.notes += f"\n\n{form.cleaned_data['date']}\n{form.cleaned_data['note']}"
        object.save()

    @add_form_to_action(NoteActionForm, display_queryset=False)
    @confirm_action(display_queryset=False)
    def add_notes_with_confirmation_many(self, request, queryset, form=None):
        for object in queryset:
            object.notes += f"\n\n{form.cleaned_data['date']}\n{form.cleaned_data['note']}"
            object.save()

    @add_form_to_action(NoteActionForm)
    @confirm_action(display_form=False)
    def add_notes_with_confirmation_no_form(self, request, queryset, form=None):
        for object in queryset:
            object.notes += f"\n\n{form.cleaned_data['date']}\n{form.cleaned_data['note']}"
            object.save()

    @add_form_to_action(NoteActionForm)
    @confirm_action()
    def add_notes_with_confirmation(self, request, object, form=None):
        object.notes += f"\n\n{form.cleaned_data['date']}\n{form.cleaned_data['note']}"
        object.save()

    @add_form_to_action(NoteActionForm)
    @add_form_to_action(NoteClearForm)
    @confirm_action()
    def add_notes_with_clear(self, request, object, forms=None):
        add_form = forms[0]
        reset_form = forms[1]
        if reset_form.cleaned_data["clear_notes"]:
            object.notes = ""
        object.notes += f"\n\n{add_form.cleaned_data['date']}\n{add_form.cleaned_data['note']}"
        object.save()
