from django import forms

from .models import LeaveEntry, LeaveType


class LeaveEntryForm(forms.ModelForm):
    class Meta:
        model = LeaveEntry
        fields = ["date", "leave_type", "half_day", "notes"]
        widgets = {
            "date": forms.DateInput(attrs={"type": "date"}),
            "notes": forms.Textarea(attrs={"rows": 3}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["leave_type"].choices = LeaveType.choices()
