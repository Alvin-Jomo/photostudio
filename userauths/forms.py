from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from userauths.models import User, Profile
import re


class UserRegisterForm(UserCreationForm):
    phone = forms.CharField(
        max_length=10,
        widget=forms.TextInput(attrs={'placeholder': 'phone No. eg., 07*** 0r 01*** format'}),
        help_text="Enter a valid 10-digit phone number starting with 07 or 01."
    )
    username = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"username"}))
    password1 = forms.CharField(widget=forms.TextInput(attrs={"placeholder":"Enter password"}))
    password2= forms.CharField(widget=forms.TextInput(attrs={"placeholder":"confirm password"}))


    class Meta:
        model = User
        fields = ['username', 'phone', 'password1', 'password2']

    def clean_phone(self):
        phone = self.cleaned_data.get("phone")
        if not re.match(r"^(07|01)\d{8}$", phone):
            raise forms.ValidationError("Phone number must start with 07 or 01 and be exactly 10 digits.")
        return phone



class ProfileForm(forms.ModelForm):
    full_name = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Full Name"}), required=False
    )
    bio = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Bio"}), required=False
    )
    phone = forms.CharField(
        widget=forms.TextInput(attrs={"placeholder": "Phone"}), required=False
    )

    class Meta:
        model = Profile
        fields = ['full_name', 'image', 'bio', 'phone']