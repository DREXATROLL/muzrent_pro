from django.contrib import admin
from .models import *

# Простой способ зарегистрировать всё
@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Brand)
admin.site.register(Location)
admin.site.register(UserProfile)
admin.site.register(InstrumentPhoto)
admin.site.register(Payment)
admin.site.register(Review)
admin.site.register(Maintenance)

@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'brand', 'category', 'price_per_day', 'status', 'location')
    list_filter = ('status', 'brand', 'category')
    search_fields = ('name', 'inventory_number')

@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'user', 'start_date', 'total_price', 'is_active')
    list_filter = ('is_active',)