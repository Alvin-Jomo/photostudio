from django.db import models
from django.contrib.auth.models import User
from django.utils.text import slugify
from django.urls import reverse

class PhotoCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True, blank=True)
    description = models.TextField(blank=True)
    cover_image = models.ImageField(upload_to='category_covers/', blank=True, null=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('studio:portfolio_by_category', kwargs={'category_slug': self.slug})

class Photo(models.Model):
    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    category = models.ForeignKey(PhotoCategory, on_delete=models.CASCADE, related_name='photos')
    image = models.ImageField(upload_to='portfolio/')
    description = models.TextField(blank=True)
    upload_date = models.DateTimeField(auto_now_add=True)
    featured = models.BooleanField(default=False)
    price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    discount_price = models.DecimalField(max_digits=8, decimal_places=2, null=True, blank=True)
    discount_active = models.BooleanField(default=False)
    tags = models.ManyToManyField('Tag', blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.title
    
    def current_price(self):
        return self.discount_price if self.discount_active else self.price
    
    def get_absolute_url(self):
        return reverse('studio:photo_detail', kwargs={'pk': self.pk})
    
   
class Service(models.Model):
    name = models.CharField(max_length=200)
    slug = models.SlugField(max_length=200, unique=True, blank=True)
    description = models.TextField()
    base_price = models.DecimalField(max_digits=8, decimal_places=2)
    duration = models.DurationField()
    cover_image = models.ImageField(upload_to='service_covers/', blank=True, null=True)
    available = models.BooleanField(default=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name
    
    def get_absolute_url(self):
        return reverse('studio:services')

class ContactUs(models.Model):
    full_name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"{self.full_name} - {self.subject}"
    
    class Meta:
        verbose_name = 'Contact Us'
        verbose_name_plural = 'Contact Us Messages'

class Tag(models.Model):
    name = models.CharField(max_length=50, unique=True)
    slug = models.SlugField(max_length=50, unique=True, blank=True)
    
    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)
    
    def __str__(self):
        return self.name

class Complaint(models.Model):
    name = models.CharField(max_length=100)  # Customer name
    contact = models.CharField(max_length=15)  # Customer contact
    message = models.TextField()  # Complaint message
    image = models.ImageField(upload_to='complaint_images/', blank=True, null=True)  # Optional image
    video = models.FileField(upload_to='complaint_videos/', blank=True, null=True)  # Optional video (e.g., MP4)
    response = models.TextField(blank=True, null=True)  # Admin response
    date_submitted = models.DateTimeField(auto_now_add=True)  # Submission date
    date_responded = models.DateTimeField(blank=True, null=True)  # Response date (set when admin responds)

    def __str__(self):
        return f"Complaint from {self.name} - Room {self.room_number}"

