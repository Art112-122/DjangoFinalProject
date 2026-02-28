from django import forms
from .models import Service, Review


class ServiceForm(forms.ModelForm):
    class Meta:
        model = Service
        fields = ["game", "title", "description", "price", "image"]

        widgets = {
            "game": forms.Select(attrs={"class": "form-select"}),
            "title": forms.TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Например: Прокачка уровня 1-50; Керамбит голд",
                }
            ),
            "description": forms.Textarea(attrs={"class": "form-control", "rows": 4}),
            "price": forms.NumberInput(attrs={"class": "form-control", "step": "0.01"}),
            "image": forms.FileInput(attrs={"class": "form-control"}),
        }


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ["rating", "text"]
        widgets = {
            "rating": forms.Select(
                choices=[(i, f"{i} ★") for i in range(5, 0, -1)],
                attrs={"class": "form-select"},
            ),
            "text": forms.Textarea(
                attrs={
                    "class": "form-control",
                    "rows": 4,
                    "placeholder": "Ваш отзыв...",
                }
            ),
        }
