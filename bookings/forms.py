from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'notes', 'coupon_code']  # Make sure coupon_code is included if using it
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['booking_date'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control'
        })
        self.fields['notes'].widget = forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control'
        })
        self.fields['coupon_code'].required = False