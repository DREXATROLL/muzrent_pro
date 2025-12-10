from django.contrib import admin
from django.urls import path, include
from django.contrib.auth import views as auth_views
from rentals import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Главная и профиль
    path('', views.catalog, name='catalog'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    
    # Стандартный вход/выход Django
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # API
    path('api/book/', views.create_booking_async, name='book_api'),
    path('api/v1/instruments/', views.api_instruments, name='api_instruments'), # Для отчета
    path('api/status/', views.api_check_availability, name='api_check_status'),
    
    path('rental/cancel/<int:rental_id>/', views.cancel_rental, name='cancel_rental'),
    path('instrument/<int:pk>/', views.instrument_detail, name='instrument_detail'),
]