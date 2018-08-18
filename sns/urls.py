from django.urls import include, path
from . import views

app_name = 'sns'

urlpatterns = [
    path('', views.index, name='index'),
    path('find_post/', views.add_post, name='find_post'),
    path('add_post/', views.add_post, name='add_post'),
    path('delete_post/', views.delete_post, name='delete_post'),
]
