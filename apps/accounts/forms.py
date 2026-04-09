from django import forms
from django.contrib.auth import get_user_model
from .models import Role

User = get_user_model()


class RegisterForm(forms.ModelForm):
    password1 = forms.CharField(
        label='Парола',
        widget=forms.PasswordInput
    )
    password2 = forms.CharField(
        label='Повтори парола',
        widget=forms.PasswordInput
    )

    class Meta:
        model = User
        fields = ['email', 'full_name']

    def clean(self):
        cleaned = super().clean()
        if cleaned.get('password1') != cleaned.get('password2'):
            raise forms.ValidationError('Паролите не съвпадат')
        return cleaned

    def save(self, commit=True):
        user = super().save(commit=False)

        # 🔒 Задаваме паролата правилно
        user.set_password(self.cleaned_data['password1'])

        # 🧑‍💻 АВТОМАТИЧНО: роля ГРАЖДАНИН
        citizen_role, _ = Role.objects.get_or_create(
            name='CITIZEN',
            defaults={'description': 'Гражданин'}
        )
        user.role = citizen_role

        if commit:
            user.save()
        return user
