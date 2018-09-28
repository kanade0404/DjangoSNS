from django.urls import path, include
from django.views.generic import TemplateView, DetailView
from . import views
from rest_framework import routers
from rest_framework.schemas import get_schema_view

app_name = 'sns'

# urlpatterns = [
#     path('', MessageViewSet.as_view(), name='index'),
#     path('', views.index, name='index'),
#     path('find_post/', views.find_post, name='find_post'),
#     path('add_post/', views.add_post, name='add_post'),
#     path('delete_post/', views.delete_post, name='delete_post'),
#     path('user_info/<int:pk>/', views.UpdateUserInfo.as_view(), name='user_info'),
# ]
router = routers.DefaultRouter()
router.register(r'messages', views.MessageViewSet)
router.register('users', views.UserViewSet)

urlpatterns = [
    path('api/', include(router.urls)),
]
