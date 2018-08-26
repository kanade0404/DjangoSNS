from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('signup/', views.UserCreate.as_view(), name='signup'),
    # path('signup/done/', views.UserCreateDone.as_view(), name='signup_done'),
    path('signup/complete/', views.UserCreateComplete.as_view(), name='signup_complete'),
]
