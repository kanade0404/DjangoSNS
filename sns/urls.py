from django.urls import path, include
from . import views

app_name = 'sns'

urlpatterns = [
    path('', views.index, name='index'),
    # path('accounts/', include('django.contrib.auth.urls')),
    # path('groups', views.groups, name='groups'),
    # path('add', views.add, name='add'),
    # path('creategroup', views.create_group, name='creategroup'),
    # path('post', views.post, name='post'),
    # path('share/<int:share_id>', views.share, name='share'),
    # path('good/<int:good_id>', views.good, name='good'),
]
