from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from studio.models import Service

class Booking(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    client = models.ForeignKey(User, on_delete=models.CASCADE, related_name='bookings')
    service = models.ForeignKey(Service, on_delete=models.CASCADE, related_name='bookings')
    booking_date = models.DateTimeField()
    created_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    notes = models.TextField(blank=True)
    coupon_code = models.CharField(max_length=20, blank=True)
    final_price = models.DecimalField(max_digits=8, decimal_places=2)
    paid = models.BooleanField(default=False)
    
    class Meta:
        ordering = ['-booking_date']
    
    def __str__(self):
        return f"{self.client.username} - {self.service.name} - {self.booking_date.strftime('%Y-%m-%d %H:%M')}"
    
    def is_upcoming(self):
        return self.booking_date > timezone.now() and self.status in ['pending', 'confirmed']

class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField()
    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()
    active = models.BooleanField(default=True)
    max_uses = models.PositiveIntegerField(default=1)
    times_used = models.PositiveIntegerField(default=0)
    
    def __str__(self):
        return self.code
    
    def is_valid(self):
        now = timezone.now()
        return (self.active and 
                self.valid_from <= now <= self.valid_to and 
                self.times_used < self.max_uses)