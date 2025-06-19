from django.contrib import admin
from .models import Photo, PhotoCategory, Service, Tag

@admin.register(Photo)
class PhotoAdmin(admin.ModelAdmin):
    list_display = ('title', 'category', 'upload_date', 'featured', 'current_price')
    list_filter = ('category', 'featured', 'upload_date')
    search_fields = ('title', 'description')
    prepopulated_fields = {'slug': ('title',)}
    readonly_fields = ('current_price',)
    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'category', 'image')
        }),
        ('Details', {
            'fields': ('description', 'tags', 'featured')
        }),
        ('Pricing', {
            'fields': ('price', 'discount_price', 'discount_active')
        }),
    )

@admin.register(PhotoCategory)
class PhotoCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ('name', 'base_price', 'duration', 'available')
    list_editable = ('available',)
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}