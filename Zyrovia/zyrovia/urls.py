from django.conf import settings
from django.conf.urls.static import static
from django.contrib import admin
from django.urls import include, path

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.core.urls')),
    path('users/', include('apps.users.urls')),
    path('nearride/', include('apps.nearride.urls')),
    path('nearshop/', include('apps.nearshop.urls')),
    path('nearservice/', include('apps.nearservice.urls')),
    path('control/', include('apps.control.urls')),
    path('locations/', include('apps.locations.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

handler400 = 'apps.core.views.bad_request_view'
handler403 = 'apps.core.views.permission_denied_view'
handler404 = 'apps.core.views.not_found_view'
handler500 = 'apps.core.views.server_error_view'
