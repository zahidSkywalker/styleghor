from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.views.generic import RedirectView

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('shop.urls')),
    path('users/', include('users.urls')),
]

# Add media and static files URLs for development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

# Redirect root to shop home
urlpatterns += [
    path('', RedirectView.as_view(pattern_name='shop:home', permanent=False)),
]
