"""hnclone URL Configuration
"""
from ratelimit.exceptions import Ratelimited
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.http import HttpResponse

urlpatterns = [
    path('', include('news.urls')),
    path('', include('accounts.urls')),
    path('digest/', include('emaildigest.urls')),
    path('admin/', admin.site.urls),
    path('health/', include('health_check.urls')),
] + static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

if settings.DEBUG:
    import debug_toolbar
    urlpatterns = [
        path('__debug__/', include(debug_toolbar.urls)),
    ] + urlpatterns


def handler403(request, exception=None):
    if isinstance(exception, Ratelimited):
        return HttpResponse("Sorry, we're not able to serve your requests this quickly.", status=429)
    return HttpResponseForbidden('Forbidden')
