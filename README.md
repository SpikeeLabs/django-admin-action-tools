# Django Admin Confirm

[![PyPI](https://img.shields.io/pypi/v/django-admin-action-tools?color=blue)](https://pypi.org/project/django-admin-action-tools/)
![Tests Status](https://github.com/SpikeeLabs/django-admin-action-tools/actions/workflows/.github/workflows/test.yml/badge.svg)
[![codecov](https://codecov.io/gh/SpikeeLabs/django-admin-action-tools/branch/main/graph/badge.svg?token=NK5V6YMWW0)](https://codecov.io/gh/SpikeeLabs/django-admin-action-tools)
![PyPI - Python Version](https://img.shields.io/pypi/pyversions/django-admin-action-tools)
![PyPI - Django Version](https://img.shields.io/pypi/djversions/django-admin-action-tools)
![PyPI - License](https://img.shields.io/pypi/l/django_admin_action_tools)

## Features
- [ ] AdminConfirmMixin
    Based on [django-admin-confirm](https://github.com/TrangPham/django-admin-confirm) with support for [django-object-actions](https://github.com/crccheck/django-object-actions)
    AdminConfirmMixin is a mixin for ModelAdmin to add confirmations to change, add and actions.
- [ ] AdminFormMixin
    AdminFormMixin is a mixin for ModelAdmin to add a form to configure your actions.


## ScreenShot
![Screenshot of Change Confirmation Page](https://raw.githubusercontent.com/SpikeeLabs/django-admin-action-tools/alpha/docs/images/screenshot.png)

![Screenshot of Add Confirmation Page](https://raw.githubusercontent.com/SpikeeLabs/django-admin-action-tools/alpha/docs/images/screenshot_confirm_add.png)

![Screenshot of Action Confirmation Page](https://raw.githubusercontent.com/SpikeeLabs/django-admin-action-tools/alpha/docs/images/screenshot_confirm_action.png)


## Installation

Install django-admin-action-tools by running:

    poetry add django-admin-action-tools

Add to INSTALLED_APPS in your project settings before `django.contrib.admin`:

    INSTALLED_APPS = [
        ...
        'admin_action_tools',

        'django.contrib.admin',
        ...
    ]

Note that this project follows the template override rules of Django.
To override a template, your app should be listed before `admin_confirm`, `admin_form` in INSTALLED_APPS.

## Configuration Options

**Environment Variables**:

Caching is used to cache files for confirmation. When change/add is submitted on the ModelAdmin, if confirmation is required, files will be cached until all validations pass and confirmation is received.

- `ADMIN_CONFIRM_CACHE_TIMEOUT` _default: 1000_
- `ADMIN_CONFIRM_CACHE_KEY_PREFIX` _default: admin_confirm\_\_file_cache_

**Attributes:**

- `confirm_change` _Optional[bool]_ - decides if changes should trigger confirmation
- `confirm_add` _Optional[bool]_ - decides if additions should trigger confirmation
- `confirmation_fields` _Optional[Array[string]]_ - sets which fields should trigger confirmation for add/change. For adding new instances, the field would only trigger a confirmation if it's set to a value that's not its default.
- `change_confirmation_template` _Optional[string]_ - path to custom html template to use for change/add
- `action_confirmation_template` _Optional[string]_ - path to custom html template to use for actions

Note that setting `confirmation_fields` without setting `confirm_change` or `confirm_add` would not trigger confirmation for change/add. Confirmations for actions does not use the `confirmation_fields` option.

**Method Overrides:**
If you want even more control over the confirmation, these methods can be overridden:

- `get_confirmation_fields(self, request: HttpRequest, obj: Optional[Object]) -> List[str]`
- `render_change_confirmation(self, request: HttpRequest, context: dict) -> TemplateResponse`
- `render_action_confirmation(self, request: HttpRequest, context: dict) -> TemplateResponse`

## Usage

### AdminConfirmMixin
It can be configured to add a confirmation page on ModelAdmin upon:

- saving changes
- adding new instances
- performing actions

**Confirm Change:**

```py
    from admin_confirm import AdminConfirmMixin

    class MyModelAdmin(AdminConfirmMixin, ModelAdmin):
        confirm_change = True
        confirmation_fields = ['field1', 'field2']
```

This would confirm changes on changes that include modifications on`field1` and/or `field2`.

**Confirm Add:**

```py
    from admin_confirm import AdminConfirmMixin

    class MyModelAdmin(AdminConfirmMixin, ModelAdmin):
        confirm_add = True
        confirmation_fields = ['field1', 'field2']
```

This would confirm add on adds that set `field1` and/or `field2` to a non default value.

Note: `confirmation_fields` apply to both add/change confirmations.

**Confirm Action:**

```py
    from admin_confirm import AdminConfirmMixin

    class MyModelAdmin(AdminConfirmMixin, ModelAdmin):
        actions = ["action1", "action2"]

        def action1(modeladmin, request, queryset):
            # Do something with the queryset

        @confirm_action
        def action2(modeladmin, request, queryset):
            # Do something with the queryset

        action2.allowed_permissions = ('change',)
```

This would confirm `action2` but not `action1`.

Action confirmation will respect `allowed_permissions` and the `has_xxx_permission` methods.

> Note: AdminConfirmMixin does not confirm any changes on inlines

### AdminFormMixin
TODO


## Development
Check out our [development process](docs/development_process.md) if you're interested.
