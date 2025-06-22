from django.urls import path
from .views import CreateBookingView, CancelBookingView, BookingConfirmationView, UserBookingsView, validate_coupon, select_service

app_name = 'bookings'

urlpatterns = [
    path('create/', select_service, name='create_booking'),
    path('create/<int:service_id>/', CreateBookingView.as_view(), name='create_booking'),
    path('confirmation/<int:pk>/', BookingConfirmationView.as_view(), name='booking_confirmation'),
    path('my-bookings/', UserBookingsView.as_view(), name='user_bookings'),
    path('validate-coupon/', validate_coupon, name='validate_coupon'),
    path('<int:pk>/cancel/', CancelBookingView.as_view(), name='cancel_booking'),  # Fixed URL pattern
]