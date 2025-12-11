from django.contrib import admin
from django.urls import path, re_path
from django.conf import settings
from django.conf.urls.static import static
from django.views.static import serve # <--- Важный импорт для раздачи файлов
from django.contrib.auth import views as auth_views
from rentals import views

urlpatterns = [
    path('admin/', admin.site.urls),
    
    # Главная и профиль
    path('', views.catalog, name='catalog'),
    path('profile/', views.profile, name='profile'),
    path('register/', views.register, name='register'),
    
    # Вход/Выход
    path('login/', auth_views.LoginView.as_view(template_name='registration/login.html'), name='login'),
    path('logout/', auth_views.LogoutView.as_view(next_page='/'), name='logout'),
    
    # API
    path('api/book/', views.create_booking_async, name='book_api'),
    path('api/v1/instruments/', views.api_instruments, name='api_instruments'),
    path('api/status/', views.api_check_availability, name='api_check_status'),

    # Новые функции (отмена, детали)
    path('rental/cancel/<int:rental_id>/', views.cancel_rental, name='cancel_rental'),
    path('instrument/<int:pk>/', views.instrument_detail, name='instrument_detail'),

    # --- медиа ---
    re_path(r'^media/(?P<path>.*)$', serve, {
        'document_root': settings.MEDIA_ROOT,
    }),
] 

# Дополнительная страховка для локальной разработки
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)