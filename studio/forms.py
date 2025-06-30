from django import forms
from .models import Complaint

class ContactForm(forms.Form):
    name = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your name'
    }))
    email = forms.EmailField(widget=forms.EmailInput(attrs={
        'class': 'form-control',
        'placeholder': 'Your email'
    }))
    subject = forms.CharField(max_length=100, widget=forms.TextInput(attrs={
        'class': 'form-control',
        'placeholder': 'Subject'
    }))
    message = forms.CharField(widget=forms.Textarea(attrs={
        'class': 'form-control',
        'rows': 5,
        'placeholder': 'Your message...'
    }))

class ComplaintForm(forms.ModelForm):
    class Meta:
        model = Complaint
        fields = ['name',  'message', 'image', 'video']

    def clean_video(self):
        video = self.cleaned_data.get('video')
        if video:
            max_size = 10 * 1024 * 1024  # 10MB
            if video.size > max_size:
                raise forms.ValidationError("Video file size should not exceed 10MB.")
        return video
