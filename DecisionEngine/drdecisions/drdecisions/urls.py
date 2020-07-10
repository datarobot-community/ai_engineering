# APIwrapper URL Configuration

from baton.autodiscover import admin
from django.conf import settings
from django.urls import include, path

from django.conf.urls.static import static
from django.contrib.staticfiles.views import serve
from django.views.decorators.cache import cache_control

urlpatterns = [
    path('', admin.site.urls),
    path('', include('datarobotapiwrapper.urls')),
    path('baton/', include('baton.urls')),

]

if settings.DEBUG:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT, view=cache_control(no_cache=True, must_revalidate=True)(serve))