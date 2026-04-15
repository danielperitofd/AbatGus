from django import forms
from django.utils.translation import gettext_lazy as _

from accounts.models import User
from access.models import Module, UserModuleAccess


class AccessUserSelectForm(forms.Form):
    user = forms.ModelChoiceField(label=_("Usuario"), queryset=User.objects.none())

    def __init__(self, *args, **kwargs):
        user_queryset = kwargs.pop("user_queryset", User.objects.none())
        super().__init__(*args, **kwargs)
        self.fields["user"].queryset = user_queryset
        self.fields["user"].widget.attrs["class"] = "form-select"


class UserModuleAccessForm(forms.Form):
    user_id = forms.IntegerField(widget=forms.HiddenInput)

    def __init__(self, *args, **kwargs):
        modules = kwargs.pop("modules", [])
        access_map = kwargs.pop("access_map", {})
        super().__init__(*args, **kwargs)
        for module in modules:
            access = access_map.get(module.id)
            self.fields[f"module_{module.id}"] = forms.BooleanField(
                label=module.name,
                required=False,
                initial=access.can_view if access else False,
            )
            self.fields[f"module_{module.id}"].widget.attrs["class"] = "form-check-input"
            self.fields[f"module_{module.id}"].widget.attrs["role"] = "switch"

    def save(self, user, modules):
        access_map = {access.module_id: access for access in UserModuleAccess.objects.filter(user=user)}
        for module in modules:
            enabled = self.cleaned_data.get(f"module_{module.id}", False)
            access = access_map.get(module.id)
            if not access:
                access = UserModuleAccess(user=user, module=module)
            access.can_view = enabled
            if not enabled:
                access.can_add = False
                access.can_change = False
                access.can_delete = False
            else:
                access.can_add = True
                access.can_change = True
            access.save()
