from django.contrib import admin
from .models import Booking, Coupon

@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ('id', 'client', 'service', 'booking_date', 'status', 'final_price')
    list_filter = ('status', 'service', 'booking_date')
    search_fields = ('client__username', 'service__name', 'coupon_code')
    date_hierarchy = 'booking_date'
    readonly_fields = ('final_price',)
    fieldsets = (
        ('Booking Info', {
            'fields': ('client', 'service', 'booking_date')
        }),
        ('Status', {
            'fields': ('status', 'notes')
        }),
        ('Pricing', {
            'fields': ('coupon_code', 'final_price')
        }),
    )

@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount_amount', 'valid_from', 'valid_to', 'active', 'times_used')
    list_filter = ('active',)
    search_fields = ('code',)