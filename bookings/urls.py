from django.urls import path
from . import views

app_name = 'bookings'

urlpatterns = [
    path('create/<int:service_id>/', views.CreateBookingView.as_view(), name='create_booking'),
    path('confirmation/<int:pk>/', views.BookingConfirmationView.as_view(), name='booking_confirmation'),
    path('my-bookings/', views.UserBookingsView.as_view(), name='user_bookings'),
    path('validate-coupon/', views.validate_coupon, name='validate_coupon'),
]