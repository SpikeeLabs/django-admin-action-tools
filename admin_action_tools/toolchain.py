from __future__ import annotations

import functools
from typing import Dict, Optional, Tuple

from django.http import HttpRequest

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
        self.ensure_default()

    def ensure_default(self):
        self.session.setdefault("toolchain", {})
        self.session["toolchain"].setdefault("history", [])

    def get_toolchain(self) -> Dict:
        return self.session.get("toolchain", {})

    def set_tool(self, tool_name: str, data: dict, metadata=None) -> None:
        self.session["toolchain"]["history"].append(tool_name)
        cleaned_data = self.__clean_data(data, metadata)
        self.session["toolchain"].update({tool_name: cleaned_data})
        self.session.modified = True

    def get_tool(self, tool_name: str) -> Tuple[Optional[dict], Optional[dict]]:
        tool = self.session.get("toolchain", {}).get(tool_name, {})
        return tool.get("data"), tool.get("metadata")

    def clear_tool_chain(self):
        self.session.pop("toolchain", None)

    def is_rollback(self):
        return BACK in self.request.POST

    def is_cancel(self):
        return CANCEL in self.request.POST

    def rollback(self):
        tool_name = self.session["toolchain"]["history"].pop()
        data, _ = self.get_tool(tool_name)
        del self.session["toolchain"][tool_name]
        self.session.modified = True
        return data

    def is_first_tool(self):
        self.ensure_default()
        return not self.session["toolchain"]["history"]

    def get_next_step(self, tool_name: str) -> ToolAction:
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

    def __clean_data(self, data, metadata):
        data = data.dict()
        data.pop("csrfmiddlewaretoken", None)
        metadata = metadata or {}
        return {"data": data, "metadata": metadata}

    def get_history(self):
        self.ensure_default()
        return self.session["toolchain"]["history"]
