from typing import List, Optional, Union

from django.contrib.admin.options import IS_POPUP_VAR
from django.db.models import Model, QuerySet
from django.http import HttpRequest

from admin_action_tools.file_cache import FileCache


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
