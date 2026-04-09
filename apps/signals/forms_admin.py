from django import forms
from .models import Signal
from apps.core.choices import SignalStatus


class AdminSignalStatusForm(forms.ModelForm):
    class Meta:
        model = Signal
        fields = ["status"]

        widgets = {
            "status": forms.Select(attrs={
                "class": "admin-status-select"
            })
        }

        labels = {
            "status": "Статус на сигнала"
        }
