from django.urls import path, include
from . import views

app_name = 'sns'

urlpatterns = [
    path('', views.index, name='index'),
]

from django.conf import settings
from django.conf.urls.static import static

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
