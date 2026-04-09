from django import forms
from .models import Signal, SignalImage
from .models import Comment

class SignalForm(forms.ModelForm):
    class Meta:
        model = Signal
        fields = [
            'title',
            'description',
            'category',
            'address',
            'latitude',
            'longitude',
        ]

        widgets = {
            'description': forms.Textarea(attrs={'rows': 4}),
            'latitude': forms.NumberInput(attrs={
                'step': '0.000001',
                'placeholder': 'Географска ширина'
            }),
            'longitude': forms.NumberInput(attrs={
                'step': '0.000001',
                'placeholder': 'Географска дължина'
            }),
        }

        labels = {
            'title': 'Заглавие',
            'description': 'Описание',
            'category': 'Категория',
            'address': 'Адрес / ориентир',
        }

    def clean(self):
        cleaned_data = super().clean()
        lat = cleaned_data.get('latitude')
        lng = cleaned_data.get('longitude')

        # 🔒 ВАЛИДАЦИЯ: задължително да е избрано място на картата
        if not lat or not lng:
            raise forms.ValidationError(
                'Моля, изберете място на картата.'
            )

        return cleaned_data


class SignalManageForm(forms.ModelForm):
    class Meta:
        model = Signal
        fields = ['status']

        labels = {
            'status': 'Статус на сигнала'
        }

        widgets = {
            'status': forms.Select(attrs={
                'class': 'form-control'
            })
        }

class AdminCommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ["content"]

        labels = {
            "content": "Добави коментар"
        }

        widgets = {
            "content": forms.Textarea(attrs={
                "rows": 3,
                "class": "form-control"
            })
        }