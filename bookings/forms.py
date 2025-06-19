from django import forms
from .models import Booking
from studio.models import Service
from django.utils import timezone
from django.core.exceptions import ValidationError

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'notes']
        widgets = {
            'booking_date': forms.DateTimeInput(attrs={
                'class': 'form-control',
                'placeholder': 'Select date and time'
            }),
            'notes': forms.Textarea(attrs={
                'rows': 3,
                'class': 'form-control',
                'placeholder': 'Any special requests or notes...'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['booking_date'].label = "Date & Time"
        self.fields['notes'].label = "Additional Notes"
    
    def clean_booking_date(self):
        booking_date = self.cleaned_data.get('booking_date')
        if booking_date and booking_date < timezone.now():
            raise ValidationError("Booking date cannot be in the past")
        return booking_date