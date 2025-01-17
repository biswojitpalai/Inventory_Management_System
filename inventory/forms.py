from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from .models import *

class UserRegistrationForm(UserCreationForm):
    email=forms.EmailField()
    class Meta:
        model=User
        fields=['username','email','password1','password2']

class InventoryItemForm(forms.ModelForm):
    new_category = forms.CharField(
        max_length=100,
        required=False,
        help_text="Enter a new category name if not in the list."
    )
    category = forms.ModelChoiceField(
        queryset=Category.objects.all(),
        required=False,
        empty_label="Select an existing category",
        label=False
    )

    class Meta:
        model = InventoryItem
        fields = ['name', 'quantity', 'category', 'price']

    def clean(self):
        cleaned_data = super().clean()
        category = cleaned_data.get("category")
        new_category = cleaned_data.get("new_category")

        if not category and not new_category:
            raise ValidationError("Please select an existing category or provide a new one.")

        return cleaned_data
