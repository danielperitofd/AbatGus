from django import forms

from .models import Organization


class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            if isinstance(field.widget, forms.CheckboxInput):
                field.widget.attrs["class"] = "form-check-input"
                field.widget.attrs["role"] = "switch"
            else:
                field.widget.attrs["class"] = "form-select" if isinstance(field.widget, forms.Select) else "form-control"

    class Meta:
        model = Organization
        fields = [
            "name",
            "legal_name",
            "document_number",
            "contact_email",
            "phone",
            "logo",
            "default_currency",
            "default_language",
            "primary_color",
            "secondary_color",
            "is_active",
        ]
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
        }
