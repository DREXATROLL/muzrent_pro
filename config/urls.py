from django.contrib import admin
from django.urls import path
from rentals import views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', views.catalog, name='catalog'),
    path('api/book/', views.create_booking_async, name='book_api'),
]