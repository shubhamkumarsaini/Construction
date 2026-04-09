from django.urls import path
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView
from .views import *
from .forms import CustomSetPasswordForm


urlpatterns = [
    path('',signup_page,name='signup'),
    path('login/', login_page, name='login'),
    path('logout/', logout_page, name='logout'),
    path('password-reset/', 
         PasswordResetView.as_view(
             template_name='account/password_reset_form.html'
         ), 
         name='password_reset'),
    
    path('password-reset-done/', 
         PasswordResetDoneView.as_view(
             template_name='account/password_reset_done.html'
         ), 
         name='password_reset_done'),
    
    path('password-reset-confirm/<uidb64>/<token>/',
        PasswordResetConfirmView.as_view(
            template_name='account/password_reset_confirm.html',
            form_class=CustomSetPasswordForm   # 👈 YE ADD KARO
        ),
        name='password_reset_confirm'),
    
    path('password-reset-complete/', 
         PasswordResetCompleteView.as_view(
             template_name='account/password_reset_complete.html'
         ), 
         name='password_reset_complete'),  
]