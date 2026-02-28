from django import forms
from django.contrib.auth.password_validation import validate_password
from django.core.validators import MinLengthValidator, MaxLengthValidator
from .models import User


class CustomUserCreationForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={"class": "form-control"}),
        label="Пароль",
    )

    username = forms.CharField(
        validators=[
            MinLengthValidator(4, message="Никнейм от 4 символов"),
            MaxLengthValidator(20, message="Никнейм до 20 символов"),
        ],
        widget=forms.TextInput(attrs={"class": "form-control"}),
    )

    def clean_password(self):
        """
        Кастомная валидация пароля через системные настройки Django.
        """
        password = self.cleaned_data.get("password")
        username = self.cleaned_data.get("username")
        email = self.cleaned_data.get("email")

        user = User(username=username, email=email)

        if password:
            validate_password(password, user=user)

        return password

    class Meta:
        model = User
        fields = ("username", "email", "password")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user
