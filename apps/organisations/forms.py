from django import forms
from django.utils.text import slugify

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
            slug = slugify(name)[:50]

        if slug:
            original_slug = slug
            counter = 1
            while Organisation.objects.filter(slug=slug).exists():
                slug = f"{original_slug}-{counter}"
                counter += 1

        return slug


class InviteForm(forms.Form):
    email = forms.EmailField(label="Email address")
