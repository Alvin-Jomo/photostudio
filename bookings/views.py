from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.utils import timezone
from django.contrib.auth.mixins import LoginRequiredMixin
from .models import Booking, Coupon
from studio.models import Service
from .forms import BookingForm

class CreateBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/create_booking.html'
    
    def get_initial(self):
        initial = super().get_initial()
        service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        initial['service'] = service
        return initial
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['service'] = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        return context
    
    def form_valid(self, form):
        booking = form.save(commit=False)
        booking.client = self.request.user
        booking.service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        booking.final_price = self.calculate_final_price(booking)
        booking.save()
        
        self.send_booking_emails(booking)
        
        messages.success(self.request, 'Your booking has been submitted!')
        return redirect('bookings:booking_confirmation', pk=booking.pk)
    
    def calculate_final_price(self, booking):
        base_price = booking.service.base_price
        if booking.coupon_code:
            try:
                coupon = Coupon.objects.get(code=booking.coupon_code, active=True)
                if coupon.is_valid():
                    coupon.times_used += 1
                    coupon.save()
                    return base_price * (1 - coupon.discount_percent/100)
            except Coupon.DoesNotExist:
                pass
        return base_price
    
    def send_booking_emails(self, booking):
        # Email to admin
        admin_subject = f"New Booking: {booking.service.name}"
        admin_message = f"""
        New booking received:
        
        Client: {booking.client.get_full_name() or booking.client.username}
        Email: {booking.client.email}
        Service: {booking.service.name}
        Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}
        Price: ${booking.final_price}
        Notes: {booking.notes or 'None'}
        """
        send_mail(
            admin_subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        # Email to client
        client_subject = f"Booking Confirmation: {booking.service.name}"
        client_message = f"""
        Thank you for your booking!
        
        Here are your booking details:
        
        Service: {booking.service.name}
        Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}
        Price: ${booking.final_price}
        
        We'll contact you shortly to confirm your appointment.
        """
        send_mail(
            client_subject,
            client_message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.client.email],
            fail_silently=False,
        )

class BookingConfirmationView(LoginRequiredMixin, DetailView):
    model = Booking
    template_name = 'bookings/confirmation.html'
    context_object_name = 'booking'
    
    def get_queryset(self):
        return Booking.objects.filter(client=self.request.user)

class UserBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/user_bookings.html'
    context_object_name = 'bookings'
    
    def get_queryset(self):
        return Booking.objects.filter(client=self.request.user).order_by('-booking_date')

def validate_coupon(request):
    code = request.GET.get('code', '')
    service_id = request.GET.get('service_id', '')
    
    try:
        service = Service.objects.get(pk=service_id)
        coupon = Coupon.objects.get(code=code, active=True)
        
        if coupon.is_valid():
            discounted_price = service.base_price * (1 - coupon.discount_percent/100)
            return JsonResponse({
                'valid': True,
                'discount_percent': coupon.discount_percent,
                'discounted_price': round(float(discounted_price), 2),
                'message': f'{coupon.discount_percent}% discount applied!'
            })
        else:
            return JsonResponse({
                'valid': False,
                'message': 'Coupon is no longer valid'
            })
    except (Coupon.DoesNotExist, Service.DoesNotExist):
        return JsonResponse({
            'valid': False,
            'message': 'Invalid coupon code'
        })