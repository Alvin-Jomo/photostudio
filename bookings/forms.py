from django import forms
from .models import Booking

class BookingForm(forms.ModelForm):
    class Meta:
        model = Booking
        fields = ['booking_date', 'notes', 'coupon_code']
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # DateTime field with better attributes
        self.fields['booking_date'].widget = forms.DateTimeInput(attrs={
            'type': 'datetime-local',
            'class': 'form-control',
            'placeholder': 'click to select date and time...',
            'min': '2024-01-01T00:00',  # Example minimum date
            'max': '2025-12-31T23:59'   # Example maximum date
        })
        
        # Notes field with placeholder and better styling
        self.fields['notes'].widget = forms.Textarea(attrs={
            'rows': 3,
            'class': 'form-control',
            'placeholder': 'Any special requests or additional information...(*optional*)',
            'style': 'resize: vertical;'  # Allow vertical resizing only
        })
        
        # Coupon code field
        self.fields['coupon_code'].required = False
        self.fields['coupon_code'].widget = forms.TextInput(attrs={
            'class': 'form-control',
            'placeholder': 'Enter coupon code (if any)...(*optional*)',
        })
        
       
        
    def clean_booking_date(self):
        """Additional validation for booking date"""
        booking_date = self.cleaned_data.get('booking_date')
        # Add your custom validation logic here if needed
        return booking_date