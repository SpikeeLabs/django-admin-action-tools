from __future__ import annotations

import functools
from datetime import datetime, timedelta
from typing import Dict, Optional, Tuple

from django.http import HttpRequest, QueryDict

from admin_action_tools.constants import BACK, CANCEL, FUNCTION_MARKER, ToolAction


def gather_tools(func):
    """
    @gather_tools function is a wrapper that is automatically added.
    It allows django-admin-action-tools to finalize the processing.
    """

    @functools.wraps(func)
    def func_wrapper(modeladmin, request, queryset_or_object):

        tool_chain: ToolChain = ToolChain(request)
        # get result
        forms = modeladmin.get_tools_result(tool_chain)
        kwargs = {}
        if len(forms) == 1:
            kwargs["form"] = forms[0]
        elif len(forms) > 1:
            kwargs["forms"] = forms

        # clear session
        tool_chain.clear_tool_chain()

        return func(modeladmin, request, queryset_or_object, **kwargs)

    return func_wrapper


def add_finishing_step(func):
    if not hasattr(func, FUNCTION_MARKER):
        setattr(func, FUNCTION_MARKER, True)
        return gather_tools(func)
    return func


class ToolChain:
    def __init__(self, request: HttpRequest) -> None:
        self.request = request
        self.session = request.session
        self.name = f"toolchain{request.path}"
        self._get_data()
        self.data.setdefault("history", [])

    def _get_data(self):
        old_data = self.session.get(self.name, {})
        expire_at = old_data.get("expire_at")

        if expire_at:
            try:
                expire_at = datetime.fromisoformat(expire_at)
            except Exception:  # pylint: disable=broad-except
                expire_at = None
                old_data = None

        if not old_data:
            self.data = {"expire_at": self._get_expiration()}
            self._save()
        elif expire_at and expire_at < datetime.now():
            self.data = {"expire_at": self._get_expiration()}
            self._save()
        else:
            self.data = old_data

    def _update_expire_at(self):
        self.data["expire_at"] = self._get_expiration()
        self._save()

    @staticmethod
    def _get_expiration():
        return (datetime.now() + timedelta(seconds=60)).isoformat()

    def _save(self):
        self.session[self.name] = self.data
        self.session.modified = True

    def get_toolchain(self) -> Dict:
        return self.data

    def set_tool(self, tool_name: str, data: dict, metadata=None) -> None:
        self.data["history"].append(tool_name)
        cleaned_data = self.__clean_data(data, metadata)
        self.data.update({tool_name: cleaned_data})
        self._save()

    def get_tool(self, tool_name: str) -> Tuple[Optional[dict], Optional[dict]]:
        tool = self.data.get(tool_name, {})
        return QueryDict(tool.get("data")), tool.get("metadata")

    def clear_tool_chain(self):
        self.session.pop(self.name, None)

    def is_rollback(self):
        return BACK in self.request.POST

    def is_cancel(self):
        return CANCEL in self.request.POST

    def rollback(self):
        tool_name = self.data["history"].pop()
        data, _ = self.get_tool(tool_name)
        del self.data[tool_name]
        self._save()
        return data

    def is_first_tool(self):
        return not self.data["history"]

    def get_next_step(self, tool_name: str) -> ToolAction:
        self._update_expire_at()
        if self.is_cancel():
            return ToolAction.CANCEL
        if self.is_rollback():
            tool_to_rollback = self.get_history()[-1]
            if tool_to_rollback != tool_name:
                return ToolAction.FORWARD
            return ToolAction.BACK
        if tool_name in self.request.POST:
            return ToolAction.CONFIRMED
        if tool_name in self.get_toolchain():
            return ToolAction.FORWARD
        return ToolAction.INIT

    def __clean_data(self, data: QueryDict, metadata):
        new_data = data.copy()
        new_data.pop("csrfmiddlewaretoken", None)

        metadata = metadata or {}
        return {"data": new_data.urlencode(), "metadata": metadata}

    def get_history(self):
        return self.data["history"]
