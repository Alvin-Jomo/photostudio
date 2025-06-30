from django.db import models
from django.contrib.auth.models import AbstractUser
from django.db.models.signals import post_save
from django.dispatch import receiver
from enum import unique
from django.db.models.signals import post_save
from django.core.validators import RegexValidator

class User(AbstractUser):
    phone_validator = RegexValidator(
        regex=r'^(07|01)\d{8}$',
        message="Phone number must start with 07 or 01 and be exactly 10 digits."
    )

    phone = models.CharField(
        max_length=10,
        unique=True,
        validators=[phone_validator],
        help_text="Enter a valid phone number starting with 07 or 01"
    )

    username = models.CharField(max_length=100, unique=True)
    bio = models.CharField(max_length=100, blank=True, null=True)

    USERNAME_FIELD = "phone"  # Authenticate with phone instead of email
    REQUIRED_FIELDS = ['username', 'email']

    def __str__(self):
        return self.username


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to="image", null=True, blank=True)
    full_name = models.CharField(max_length=200, null=True, blank=True)
    bio = models.CharField(max_length=200, null=True, blank=True)
    address = models.CharField(max_length=200, null=True, blank=True)
    # Removed phone field since it's already in User model

    def __str__(self):
        return f"{self.user.username} - {self.full_name}"

class ContactUs(models.Model):
    full_name = models.CharField(max_length=200)
    email = models.CharField(max_length=200)
    phone = models.CharField(max_length=200)
    subject = models.CharField(max_length=200)
    message = models.TextField()

    class Meta:
        verbose_name = "Contact Us"
        verbose_name_plural = "Contact Us"

    def __str__(self):
        return self.full_name

# Signals to handle Profile creation
@receiver(post_save, sender=User)
def create_user_profile(sender, instance, created, **kwargs):
    """
    Automatically create a Profile when a new User is created.
    """
    if created:
        Profile.objects.get_or_create(user=instance)

@receiver(post_save, sender=User)
def save_user_profile(sender, instance, **kwargs):
    """
    Save the Profile whenever the User is saved.
    """
    if hasattr(instance, 'profile'):
        instance.profile.save()
