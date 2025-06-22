from django import forms
from django.contrib.auth.forms import UserCreationForm
from userauths.models import User, Profile


class UserRegisterForm(UserCreationForm):
    phone = forms.CharField(
        max_length=20,
        required=True,
        widget=forms.TextInput(attrs={"placeholder": "Phone"})
    )

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']

    def save(self, commit=True):
        user = super().save(commit=False)
        if commit:
            user.save()
            # Save phone to Profile
            profile, created = Profile.objects.get_or_create(user=user)
            profile.phone = self.cleaned_data.get('phone')
            profile.save()
        return user

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
