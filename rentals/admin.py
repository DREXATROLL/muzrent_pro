from django.contrib import admin
from .models import Instrument, Rental

# Настройка отображения Инструментов
@admin.register(Instrument)
class InstrumentAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'price', 'status') # Какие колонки показывать
    list_filter = ('status', 'category') # Фильтры справа
    search_fields = ('name',) # Строка поиска

# Настройка отображения Аренд
@admin.register(Rental)
class RentalAdmin(admin.ModelAdmin):
    list_display = ('instrument', 'user', 'created_at')
    readonly_fields = ('created_at',) # Запрет на редактирование даты создания