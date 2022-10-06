from django.contrib.admin import ModelAdmin
from django.core.exceptions import ValidationError
from django.forms import ModelForm

from admin_action_tools.admin import AdminConfirmMixin
from tests.market.models import Checkout


class CheckoutForm(ModelForm):
    search_fields = ["shop", "date"]
    confirm_change = True

    class Meta:
        model = Checkout
        fields = [
            "currency",
            "shop",
            "total",
            "timestamp",
            "date",
        ]

    def clean_total(self):
        try:
            total = float(self.cleaned_data["total"])
        except Exception:
            raise ValidationError("Invalid Total From clean_total")
        if total == 111:  # Use to cause error in test
            raise ValidationError("Invalid Total 111")

        return total

    def clean(self):
        try:
            total = float(self.data["total"])
        except Exception:
            raise ValidationError("Invalid Total From clean")
        if total == 222:  # Use to cause error in test
            raise ValidationError("Invalid Total 222")

        self.cleaned_data["total"] = total


class CheckoutAdmin(AdminConfirmMixin, ModelAdmin):
    confirm_add = True
    confirm_change = True
    autocomplete_fields = ["shop"]
    form = CheckoutForm
