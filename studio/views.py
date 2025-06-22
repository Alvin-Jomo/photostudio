from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Photo, PhotoCategory, Service, Tag
from .forms import ContactForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin


class HomeView(LoginRequiredMixin, TemplateView):
    template_name = 'studio/home.html'
    login_url = 'userauths:sign-in'

    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['featured_photos'] = Photo.objects.filter(featured=True)[:8]
        context['services'] = Service.objects.filter(available=True)[:3]
        return context

class PortfolioView(ListView):
    model = Photo
    template_name = 'studio/portfolio.html'
    context_object_name = 'photos'
    
    def get_queryset(self):
        category_slug = self.kwargs.get('category_slug')
        if category_slug:
            category = get_object_or_404(PhotoCategory, slug=category_slug)
            return Photo.objects.filter(category=category)
        return Photo.objects.all()
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = PhotoCategory.objects.all()
        return context
   
class PhotoDetailView(DetailView):
    model = Photo
    template_name = 'studio/photo_detail.html'
    context_object_name = 'photo'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['related_photos'] = Photo.objects.filter(
            category=self.object.category
        ).exclude(id=self.object.id)[:4]
        return context

class ServicesView(ListView):
    model = Service
    template_name = 'studio/services.html'
    context_object_name = 'services'
    
    def get_queryset(self):
        return Service.objects.filter(available=True).order_by('base_price')

class AboutView(TemplateView):
    template_name = 'studio/about.html'

class ContactView(TemplateView):
    template_name = 'studio/contact.html'

    def get(self, request, *args, **kwargs):
        form = ContactForm()
        return render(request, self.template_name, {'form': form})

    def post(self, request, *args, **kwargs):
        form = ContactForm(request.POST)
        if form.is_valid():
            # Process the form (e.g., send email)
            self.send_contact_email(form.cleaned_data)
            messages.success(request, "Your message has been sent!")
            return redirect('studio:contact')  # Redirect to avoid resubmission
        return render(request, self.template_name, {'form': form})

    def send_contact_email(self, cleaned_data):
        subject = f"New Contact Form: {cleaned_data['subject']}"
        message = f"""
        From: {cleaned_data['name']} <{cleaned_data['email']}>

        Message:
        {cleaned_data['message']}
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )
    template_name = 'studio/contact.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        if self.request.method == 'POST':
            form = ContactForm(self.request.POST)
            if form.is_valid():
                self.send_contact_email(form.cleaned_data)
                messages.success(self.request, 'Your message has been sent!')
                return redirect('studio:contact')
        else:
            form = ContactForm()
        context['form'] = form
        return context
    
    def send_contact_email(self, cleaned_data):
        subject = f"New Contact Form Submission: {cleaned_data['subject']}"
        message = f"""
        From: {cleaned_data['name']} <{cleaned_data['email']}>
        
        Message:
        {cleaned_data['message']}
        """
        send_mail(
            subject,
            message,
            settings.DEFAULT_FROM_EMAIL,
            [settings.CONTACT_EMAIL],
            fail_silently=False,
        )


