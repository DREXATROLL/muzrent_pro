from django import forms
from django.contrib.auth.models import User
from .models import UserProfile, Review

class UserRegistrationForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput, label="Пароль")
    confirm_password = forms.CharField(widget=forms.PasswordInput, label="Повторите пароль")
    phone = forms.CharField(max_length=20, label="Телефон", required=False)
    address = forms.CharField(widget=forms.Textarea, label="Адрес", required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Пароли не совпадают")

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['rating', 'comment']
        widgets = {
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Напишите ваш отзыв...'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'min': 1, 'max': 5}),
        }
        labels = {
            'rating': 'Оценка (1-5)',
            'comment': 'Комментарий'
        }