from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)

    class Meta:
        model = User
        fields = ("username", "email", "password1", "password2")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data["email"]
        if commit:
            user.save()
        return user


class UserPreferencesForm(forms.ModelForm):
    class Meta:
        model = User
        fields = [
            "annual_leave_allowance",
            "carryover_max",
            "carryover_days",
            "week_start",
            "year_start_month",
            "year_start_day",
        ]
        widgets = {
            "year_start_month": forms.NumberInput(attrs={"min": 1, "max": 12}),
            "year_start_day": forms.NumberInput(attrs={"min": 1, "max": 31}),
        }
