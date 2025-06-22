from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import CreateView, DetailView, ListView, DeleteView
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from django.http import JsonResponse
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.utils import timezone
from .models import Booking, Coupon
from studio.models import Service
from .forms import BookingForm
from django.contrib.auth.decorators import login_required


@login_required
def select_service(request):
    """View to select a service before booking"""
    services = Service.objects.filter(available=True)
    return render(request, 'bookings/select_service.html', {'services': services})


class CreateBookingView(LoginRequiredMixin, CreateView):
    model = Booking
    form_class = BookingForm
    template_name = 'bookings/create_booking.html'
    
    def dispatch(self, request, *args, **kwargs):
        """Redirect if no service_id is provided"""
        if 'service_id' not in kwargs:
            return redirect('bookings:select_service')
        return super().dispatch(request, *args, **kwargs)
    
    def get_initial(self):
        """Prefill the service in the form"""
        initial = super().get_initial()
        service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        initial['service'] = service
        return initial
    
    def get_context_data(self, **kwargs):
        """Add service to template context"""
        context = super().get_context_data(**kwargs)
        context['service'] = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        return context
    
    def form_valid(self, form):
        """Handle valid form submission"""
        booking = form.save(commit=False)
        booking.client = self.request.user
        booking.service = get_object_or_404(Service, pk=self.kwargs.get('service_id'))
        booking.final_price = self.calculate_final_price(booking)
        booking.status = 'pending'  # Set initial status
        booking.save()
        
        self.send_booking_emails(booking)
        messages.success(self.request, 'Your booking has been submitted!')
        return redirect('bookings:booking_confirmation', pk=booking.pk)
    
    def calculate_final_price(self, booking):
        """Calculate final price with coupon if applicable"""
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
        """Send confirmation emails to admin and client"""
        # Email to admin
        admin_subject = f"New Booking: {booking.service.name}"
        admin_message = f"""
        New booking received:
        
        Client: {booking.client.get_full_name() or booking.client.username}
        Email: {booking.client.email}
        Service: {booking.service.name}
        Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}
        Price: ${booking.final_price}
        Status: {booking.get_status_display()}
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
        Status: {booking.get_status_display()}
        
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
        """Only allow users to view their own bookings"""
        return Booking.objects.filter(client=self.request.user)

def validate_coupon(request):
    """AJAX endpoint for coupon validation"""
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
        return JsonResponse({
            'valid': False,
            'message': 'Coupon is no longer valid'
        })
    except (Coupon.DoesNotExist, Service.DoesNotExist):
        return JsonResponse({
            'valid': False,
            'message': 'Invalid coupon code or service'
        })


class UserBookingsView(LoginRequiredMixin, ListView):
    model = Booking
    template_name = 'bookings/user_bookings.html'
    context_object_name = 'bookings'
    paginate_by = 10  # Add pagination
    
    def get_queryset(self):
        """Return user's bookings ordered by date"""
        return Booking.objects.filter(
            client=self.request.user
        ).order_by('-booking_date').select_related('service')

class CancelBookingView(LoginRequiredMixin, DeleteView):
    model = Booking
    success_url = reverse_lazy('bookings:user_bookings')
    http_method_names = ['post']  # Only allow POST requests
    
    def get_queryset(self):
        """Only allow users to cancel their own bookings"""
        return Booking.objects.filter(client=self.request.user)
    
    def delete(self, request, *args, **kwargs):
        """Handle booking cancellation"""
        booking = self.get_object()
        
        if booking.status not in ['pending', 'confirmed']:
            messages.error(request, "You can only cancel pending or confirmed bookings.")
            return redirect(self.get_success_url())
        
        # Update status to cancelled and save
        booking.status = 'cancelled'
        booking.cancelled_at = timezone.now()
        booking.save()
        
        # Send cancellation emails
        self.send_cancellation_emails(booking)
        
        messages.success(request, "Your booking has been cancelled successfully.")
        return redirect(self.get_success_url())
    
    def send_cancellation_emails(self, booking):
        """Send cancellation notification emails"""
        # Email to admin
        admin_subject = f"Booking Cancelled: {booking.service.name}"
        admin_message = f"""
        Booking cancelled:
        
        Client: {booking.client.get_full_name() or booking.client.username}
        Service: {booking.service.name}
        Original Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}
        Cancelled At: {timezone.now().strftime('%Y-%m-%d %H:%M')}
        """
        send_mail(
            admin_subject,
            admin_message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.ADMIN_EMAIL],
            fail_silently=False,
        )
        
        # Email to client
        client_subject = f"Booking Cancelled: {booking.service.name}"
        client_message = f"""
        Your booking has been cancelled:
        
        Service: {booking.service.name}
        Original Date: {booking.booking_date.strftime('%Y-%m-%d %H:%M')}
        
        We're sorry to see you go. Feel free to book again anytime!
        """
        send_mail(
            client_subject,
            client_message,
            settings.DEFAULT_FROM_EMAIL,
            [booking.client.email],
            fail_silently=False,
        )