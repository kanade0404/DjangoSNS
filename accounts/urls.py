from django.urls import path
from . import views

app_name = 'accounts'

urlpatterns = [
    path('login/', views.UserAuth.as_view(), name='login'),
    path('signup/', views.UserCreate.as_view(), name='signup'),
    path('signup/done/', views.UserCreateDone.as_view(), name='signup_done'),
    path('signup/complete/<token>/', views.UserCreateComplete.as_view(), name='signup_complete'),
    path('reset_password/', views.ResetPassword.as_view(), name='reset_password'),
    path('reset_password/done/', views.ResetPasswordDone.as_view(), name='reset_password_done'),
    path('reset_password/<uidb64>/<token>/', views.ResetPasswordConfirm.as_view(), name='reset_password_confirm'),
    path('reset_password/complete/', views.ResetPasswordComplete.as_view(), name='reset_password_complete'),
]
