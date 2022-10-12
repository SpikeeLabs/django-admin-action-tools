from typing import Callable, Dict

from django.contrib.admin import helpers
from django.db.models import QuerySet
from django.forms import Form
from django.http import HttpRequest

from admin_action_tools.admin.base import BaseMixin
from admin_action_tools.constants import CONFIRM_FORM
from admin_action_tools.utils import snake_to_title_case


class ActionFormMixin(BaseMixin):

    # Custom templates (designed to be over-ridden in subclasses)
    action_form_template: str = None

    def build_context(self, request: HttpRequest, func: Callable, queryset: QuerySet, form_instance: Form):
        action_display_name = snake_to_title_case(func.__name__)
        title = f"Configure Action: {action_display_name}"
        opts = self.model._meta  # pylint: disable=W0212

        return {
            **self.admin_site.each_context(request),
            "title": title,
            "action": func.__name__,
            "action_display_name": action_display_name,
            "action_checkbox_name": helpers.ACTION_CHECKBOX_NAME,
            "submit_name": "confirm_action",
            "queryset": queryset,
            "media": self.media + form_instance.media,
            "opts": opts,
            "form": form_instance,
            "submit_action": CONFIRM_FORM,
        }

    def render_action_form(self, request: HttpRequest, context: Dict):
        return super().render_template(
            request, context, "form_tool/action_form.html", custom_template=self.action_form_template
        )


def add_form_to_action(form: Form):
    """
    @add_form_to_action function wrapper for Django ModelAdmin actions
    Will redirect to a form page to ask for more information

    Next, it would call the action with the form data.
    """

    def add_form_to_action_decorator(func):
        def func_wrapper(modeladmin: ActionFormMixin, request, queryset_or_object):
            # First called by `Go` which would not have confirm_action in params
            if request.POST.get(CONFIRM_FORM):
                form_instance = form(request.POST)
                if form_instance.is_valid():
                    return func(modeladmin, request, queryset_or_object, form=form_instance)
            else:
                form_instance = form()

            queryset: QuerySet = modeladmin.to_queryset(request, queryset_or_object)
            context = modeladmin.build_context(request, func, queryset, form_instance)

            # Display form
            return modeladmin.render_action_form(request, context)

        return func_wrapper

    return add_form_to_action_decorator
