from django.shortcuts import render, get_object_or_404, redirect
from django.views.generic import ListView, DetailView, TemplateView
from django.core.paginator import Paginator
from django.contrib import messages
from django.core.mail import send_mail
from django.conf import settings
from .models import Photo, PhotoCategory, Service, Tag, ContactUs, Complaint
from .forms import ContactForm, ComplaintForm
from django.contrib.auth.decorators import login_required
from django.contrib.auth.mixins import LoginRequiredMixin

def complain_page(request):
    if request.method == 'POST':
        form = ComplaintForm(request.POST, request.FILES)
        if form.is_valid():
            complaint = form.save()
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                # Return JSON response for AJAX requests
                return JsonResponse({
                    'success': True,
                    'complaint': {
                        'name': complaint.name,
                        'message': complaint.message,
                        'image': complaint.image.url if complaint.image else None,
                        'video': complaint.video.url if complaint.video else None,
                        'date_submitted': complaint.date_submitted.strftime("%b %d, %Y %I:%M %p"),
                    }
                })
            else:
                messages.success(request, "Your complaint has been submitted successfully.")
                return render(request, 'studio/complain_page.html')
        else:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'success': False, 'errors': form.errors})
            else:
                messages.error(request, "There was an error submitting your complaint.")
    else:
        form = ComplaintForm()

    complaints = Complaint.objects.all().order_by('-date_submitted')

    context = {
        'form': form,
        'complaints': complaints,
    }
    return render(request, 'studio/complain_page.html', context)

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
        
        # Add related services (same category)
        context['related_services'] = Service.objects.filter(
            available=True
        ).order_by('base_price')[:3]  # Adjust number as needed
        
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
            try:
                # Save to database
                ContactUs.objects.create(
                    full_name=form.cleaned_data['name'],
                    email=form.cleaned_data['email'],
                    subject=form.cleaned_data['subject'],
                    message=form.cleaned_data['message']
                )
                
                self.send_contact_email(form.cleaned_data)
                messages.success(request, "Your message has been sent successfully!")
                return redirect('studio:contact')
            except Exception as e:
                messages.error(request, f"Failed to send message. Error: {str(e)}")
                return render(request, self.template_name, {'form': form})
        
        return render(request, self.template_name, {'form': form})
    
    def send_contact_email(self, cleaned_data):
        subject = f"New Contact: {cleaned_data['subject']}"
        message = f"""
        From: {cleaned_data['name']} <{cleaned_data['email']}>
        Subject: {cleaned_data['subject']}
        
        Message:
        {cleaned_data['message']}
        
        You can reply directly to {cleaned_data['email']}
        """
        
        send_mail(
            subject=subject,
            message=message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=False,
        ) 