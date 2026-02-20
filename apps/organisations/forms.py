from django import forms

from .models import Organisation


class OrganisationForm(forms.ModelForm):
    class Meta:
        model = Organisation
        fields = ["name", "slug"]
        widgets = {
            "slug": forms.TextInput(attrs={"placeholder": "Leave blank to auto-generate"}),
        }

    def clean_slug(self):
        slug = self.cleaned_data.get("slug")
        if not slug:
            name = self.cleaned_data.get("name", "")
            slug = name.lower().replace(" ", "-")[:50]
        return slug


class InviteForm(forms.Form):
    email = forms.EmailField(label="Email address")
