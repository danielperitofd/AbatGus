from django import forms

from .models import Organization


class OrganizationForm(forms.ModelForm):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        for field in self.fields.values():
            field.widget.attrs["class"] = "form-control"

    class Meta:
        model = Organization
        fields = [
            "name",
            "legal_name",
            "document_number",
            "contact_email",
            "phone",
            "logo",
            "primary_color",
            "secondary_color",
            "is_active",
        ]
        widgets = {
            "primary_color": forms.TextInput(attrs={"type": "color"}),
            "secondary_color": forms.TextInput(attrs={"type": "color"}),
        }
