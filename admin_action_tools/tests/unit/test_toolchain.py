from django.http import QueryDict

from admin_action_tools.constants import CONFIRM_FORM
from admin_action_tools.tests.helpers import AdminConfirmTestCase
from admin_action_tools.toolchain import ToolChain
from tests.market.form import NoteActionForm


class TestToolchain(AdminConfirmTestCase):
    def test_toolchain_expired(self):
        request = self.factory.request()
        name = f"toolchain{request.path}"
        request.session[name] = {
            "expire_at": "2012-11-02T15:14:31.000",
            "history": ["tool1"],
            "tool1": {"data": {"field1": True}, "metadata": {}},
        }
        toolchain = ToolChain(request)

        # test toolchain reset
        self.assertEqual(toolchain.get_history(), [])

        # test data is save
        self.assertEqual(request.session[name]["history"], [])

    def test_toolchain_wrong_date(self):
        request = self.factory.request()
        name = f"toolchain{request.path}"
        request.session[name] = {
            "expire_at": "ggg",
            "history": ["tool1"],
            "tool1": {"data": {"field1": True}, "metadata": {}},
        }
        toolchain = ToolChain(request)

        # test toolchain reset
        self.assertEqual(toolchain.get_history(), [])

        # test data is save
        self.assertEqual(request.session[name]["history"], [])

    def test_toolchain_wrong_date_type(self):
        request = self.factory.request()
        name = f"toolchain{request.path}"
        request.session[name] = {
            "expire_at": 3,
            "history": ["tool1"],
            "tool1": {"data": {"field1": True}, "metadata": {}},
        }
        toolchain = ToolChain(request)

        # test toolchain reset
        self.assertEqual(toolchain.get_history(), [])

        # test data is save
        self.assertEqual(request.session[name]["history"], [])

    def test_toolchain_querydict(self):
        data = QueryDict("a=1&a=2&a=3")
        request = self.factory.request()
        toolchain = ToolChain(request)
        res = toolchain._ToolChain__clean_data(data, {})

        self.assertEqual(res["data"], "a=1&a=2&a=3")
