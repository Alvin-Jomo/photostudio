from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Profile, ContactUs

# User Admin
class CustomUserAdmin(UserAdmin):
    list_display = ('username', 'phone', 'email', 'is_staff')
    list_filter = ('is_staff', 'is_superuser', 'is_active')
    search_fields = ('username', 'phone', 'email')
    ordering = ('username',)

# Profile Admin
class ProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'full_name', 'bio', 'address')
    list_editable = ('full_name', 'bio', 'address')
    search_fields = ('user__username', 'full_name')
    list_select_related = ('user',)

# ContactUs Admin
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'phone', 'subject')
    search_fields = ('full_name', 'email', 'subject')
    list_filter = ('subject',)

# Register your models
admin.site.register(User, CustomUserAdmin)
admin.site.register(Profile, ProfileAdmin)
admin.site.register(ContactUs, ContactUsAdmin)