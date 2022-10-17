from typing import Dict, List, Optional, Union

from django.contrib.admin.options import IS_POPUP_VAR
from django.db.models import Model, QuerySet
from django.http import HttpRequest
from django.template.response import TemplateResponse

from admin_action_tools.file_cache import FileCache
from admin_action_tools.toolchain import ToolChain


class BaseMixin:
    _file_cache = FileCache()

    actions: Optional[List[str]]

    def get_change_action(self, fieldname):
        actions = getattr(self, fieldname, [])
        change_actions = []
        for name in actions:
            func = getattr(self, name)
            description = self._get_action_description(func, name)
            change_actions.append((func, name, description))
        return change_actions

    def _get_actions(self, request):
        """
        Return a dictionary mapping the names of all actions & object actions for this
        ModelAdmin to a tuple of (callable, name, description) for each action.
        """
        # If self.actions is set to None that means actions are disabled on
        # this page.
        if self.actions is None or IS_POPUP_VAR in request.GET:
            return {}

        actions = self._get_base_actions()
        actions.extend(self.get_change_action("change_actions"))
        actions.extend(self.get_change_action("changelist_actions"))

        actions = self._filter_actions_by_permissions(request, actions)
        return {name: (func, name, desc) for func, name, desc in actions}

    def to_queryset(self, request: HttpRequest, object_or_queryset: Union[QuerySet, Model]) -> QuerySet:
        if not isinstance(object_or_queryset, QuerySet):
            return self.get_queryset(request).filter(pk=object_or_queryset.pk)
        return object_or_queryset

    def render_template(self, request: HttpRequest, context: Dict, template_name: str, custom_template=None):
        opts = self.model._meta
        app_label = opts.app_label

        request.current_app = self.admin_site.name
        tool_chain: ToolChain = ToolChain(request)
        context["first"] = tool_chain.is_first_tool()

        return TemplateResponse(
            request,
            custom_template
            or [
                f"admin/{app_label}/{opts.model_name}/{template_name}",
                f"admin/{app_label}/{template_name}",
                f"admin/{template_name}",
            ],
            context,
        )

    def get_tools_result(self, tool_chain: ToolChain):
        history = tool_chain.get_history()
        forms = []
        for tool_name in history:
            data, metadata = tool_chain.get_tool(tool_name)
            forms.append(self.load_form(data, metadata))
        return forms
