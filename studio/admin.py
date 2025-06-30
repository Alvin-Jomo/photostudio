from django.contrib import admin
from django.utils.html import format_html
from .models import Photo, PhotoCategory, Service, Tag, ContactUs, Complaint

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ( 'title','thumbnail_preview', 'category', 'upload_date', 'featured', 'current_price')
    list_filter = ('category', 'featured', 'upload_date')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('current_price', 'image_preview')
    list_per_page = 25
    list_display_links = ('thumbnail_preview', 'title')
    list_editable = ('featured',)
    
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'image', 'image_preview')
        }),
        ('Details', {
            'fields': ('description', 'tags', 'featured'),
            'classes': ('collapse', 'wide')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'discount_active', 'current_price'),
            'classes': ('collapse',)
        }),
    )

    def thumbnail_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="height: 50px; width: 50px; object-fit: cover; border-radius: 3px; border: 1px solid #ddd;" />',
                obj.image.url
            )
        return "-"
    thumbnail_preview.short_description = 'Preview'

    def image_preview(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 100%; border-radius: 5px; border: 1px solid #ddd; padding: 5px; background: white; box-shadow: 0 0 5px rgba(0,0,0,0.1);" />',
                obj.image.url
            )
        return "-"
    image_preview.short_description = 'Image Preview'


@admin.register(PhotoCategory)
class PhotoCategoryAdmin(admin.ModelAdmin):
    list_display = ( 'name', 'cover_preview', 'slug', 'description_preview')
    list_display_links = ('cover_preview', 'name')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'description')
    readonly_fields = ('cover_display',)
    list_per_page = 20
    
    fieldsets = (
        (None, {
            'fields': ('name', 'slug', 'cover_image', 'cover_display')
        }),
        ('Description', {
            'fields': ('description',),
            'classes': ('wide',)
        }),
    )

    def cover_preview(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="height: 50px; width: 50px; object-fit: cover; border-radius: 3px; border: 1px solid #ddd;" />',
                obj.cover_image.url
            )
        return "-"
    cover_preview.short_description = 'Cover'
    
    def cover_display(self, obj):
        if obj.cover_image:
            return format_html(
                '<img src="{}" style="max-height: 300px; max-width: 100%; border-radius: 5px; border: 1px solid #ddd; padding: 5px; background: white; box-shadow: 0 0 5px rgba(0,0,0,0.1);" />',
                obj.cover_image.url
            )
        return "-"
    cover_display.short_description = 'Cover Preview'
    
    def description_preview(self, obj):
        return obj.description[:75] + '...' if len(obj.description) > 75 else obj.description
    description_preview.short_description = 'Description'


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'duration', 'available')
    list_editable = ('available',)
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_filter = ('available',)
    list_per_page = 20


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name',)
    list_per_page = 20


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ('full_name', 'email', 'subject', 'created_at', 'message_preview')
    search_fields = ('full_name', 'email', 'subject')
    readonly_fields = ('message_display',)
    list_per_page = 20
    ordering = ('-created_at',)
    
    fieldsets = (
        (None, {
            'fields': ('full_name', 'email', 'subject')
        }),
        ('Message', {
            'fields': ('message_display',),
            'classes': ('wide',),
        }),
        ('Dates', {
            'fields': ('created_at',),
            'classes': ('collapse',),
        }),
    )

    def message_preview(self, obj):
        return obj.message[:50] + '...' if len(obj.message) > 50 else obj.message
    message_preview.short_description = 'Message Preview'
    
    def message_display(self, obj):
        return format_html('<div style="white-space: pre-wrap; padding: 10px; background: #f8f8f8; border-radius: 5px;">{}</div>', obj.message)
    message_display.short_description = 'Full Message'


class ComplaintAdmin(admin.ModelAdmin):
    list_display = ('name',  'date_submitted', 'date_responded', 'response', 'image_preview', 'video_preview')
    list_filter = ('date_submitted', 'date_responded')
    search_fields = ('name', 'contact', 'message', 'response')
    readonly_fields = ('date_submitted',)

    def save_model(self, request, obj, form, change):
        if obj.response and not obj.date_responded:
            obj.date_responded = timezone.now()
        super().save_model(request, obj, form, change)

    # Display Image Preview
    def image_preview(self, obj):
        if obj.image:
            return format_html('<img src="{}" width="100" height="75" style="object-fit: cover; border-radius: 5px;"/>', obj.image.url)
        return "No Image"

    image_preview.short_description = "Image Preview"

    # Display Video Preview
    def video_preview(self, obj):
        if obj.video:
            return format_html('<video width="150" height="100" controls><source src="{}" type="video/mp4">Your browser does not support the video tag.</video>', obj.video.url)
        return "No Video"

    video_preview.short_description = "Video Preview"


admin.site.register(Complaint, ComplaintAdmin)