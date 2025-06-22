from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse


def health_check(request):
    return HttpResponse("OK", content_type="text/plain")

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('studio.urls')),
    path('bookings/', include('bookings.urls')),
    path('accounts/', include('django.contrib.auth.urls')),
    path('userauths/', include('userauths.urls')),
    path('health/', health_check),  # Health check endpoint
    path('ckeditor5/', include('django_ckeditor_5.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)