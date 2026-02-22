from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import User


from django import forms
from .models import User

class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput)

    class Meta:
        model = User
        fields = ('username', 'email', 'password') # Добавляем username сюда

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"]) # Хэшируем пароль
        if commit:
            user.save()
        return user