from django.urls import path
from django.contrib.auth import views as auth_views
from . import views

urlpatterns = [
    # Default redirect to dashboard or login
    path('', views.home_redirect, name='home'),
    
    # Auth views
    path('login/', auth_views.LoginView.as_view(template_name='users/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='login'), name='logout'),
    path('signup/', views.signup, name='signup'),
    
    # Dashboard
    path('dashboard/', views.dashboard, name='dashboard'),
]
