from django import forms
from django.contrib.auth.forms import AuthenticationForm

from .models import User


class BootstrapFormMixin:
    def apply_bootstrap(self):
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
                field.widget.attrs["role"] = "switch"
            else:
                css_class = "form-select" if isinstance(field.widget, forms.Select) else "form-control"
                existing = field.widget.attrs.get("class", "")
                field.widget.attrs["class"] = f"{existing} {css_class}".strip()


class LoginForm(BootstrapFormMixin, AuthenticationForm):
    username = forms.CharField(label="Usuário")
    password = forms.CharField(label="Senha", widget=forms.PasswordInput)

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()


class UserForm(BootstrapFormMixin, forms.ModelForm):
    password = forms.CharField(
        label="Senha",
        required=False,
        widget=forms.PasswordInput(render_value=False),
        help_text="Preencha apenas para definir ou alterar a senha.",
    )

    class Meta:
        model = User
        fields = [
            "first_name",
            "last_name",
            "username",
            "email",
            "organization",
            "role",
            "job_title",
            "phone",
            "avatar",
            "internal_notes",
            "is_active",
            "password",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.apply_bootstrap()
        placeholders = {
            "first_name": "Primeiro nome",
            "last_name": "Último nome",
            "username": "Usuário",
            "email": "Endereço de email",
            "job_title": "Cargo",
            "phone": "Telefone",
            "internal_notes": "Observações internas",
            "password": "Senha",
        }
        for field_name, placeholder in placeholders.items():
            if field_name in self.fields:
                self.fields[field_name].widget.attrs.setdefault("placeholder", placeholder)
        self.fields["avatar"].help_text = "Envie um PNG ou JPG para usar no perfil."
        self.fields["avatar"].widget.attrs.update(
            {
                "accept": ".png,.jpg,.jpeg,image/png,image/jpeg",
                "data-avatar-input": "true",
            }
        )

    def save(self, commit=True):
        user = super().save(commit=False)
        password = self.cleaned_data.get("password")
        if password:
            user.set_password(password)
        elif not user.pk:
            user.set_unusable_password()
        if commit:
            user.save()
            self.save_m2m()
        return user
