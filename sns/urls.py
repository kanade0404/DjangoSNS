from django.urls import path, include
from . import views
from rest_framework import routers
from django.conf import settings
from django.conf.urls.static import static

app_name = 'sns'

urlpatterns = [
    # path('', MessageViewSet.as_view(), name='index'),
    path('', views.index, name='index'),
    # path('<int:pk>/', views.find_post, name='find_post'),
    path('update/', views.add_post, name='add_post'),
    path('delete/', views.delete_post, name='delete_post'),
    path('user_info/<int:pk>/', views.user_detail, name='user_info'),
]
# router = routers.DefaultRouter()
# router.register(r'messages', views.MessageViewSet)
# router.register(r'users', views.UserViewSet)

# urlpatterns = [
#     path('api/', include(router.urls)),  # APIへのルーティング
#     path('', views.index, name='index'),  # vueシングルページへのルーティング
# ] + static(settings.STATIC_URL)
