from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from asgiref.sync import sync_to_async
from .models import Instrument, Rental
from django.contrib.auth.models import User

# Синхронная вьюха для каталога
def catalog(request):
    instruments = Instrument.objects.all().order_by('id')
    
    category = request.GET.get('category')
    if category:
        instruments = instruments.filter(category=category)
    
    # Получаем список всех категорий для меню
    categories = Instrument.objects.values_list('category', flat=True).distinct()
    
    return render(request, 'catalog.html', {
        'instruments': instruments,
        'categories': categories
    })

# Выносим работу с юзером в отдельную функцию-обертку
@sync_to_async
def get_user_safe(request):
    # Обращение к request.user вызывает запрос в БД (сессии)
    # Поэтому это должно быть внутри sync_to_async
    if request.user.is_authenticated:
        return request.user
    # Если не залогинен, берем первого юзера (Админа) для теста
    return User.objects.first()

# Асинхронная вьюха
async def create_booking_async(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # ИСПОЛЬЗУЕМ БЕЗОПАСНУЮ ФУНКЦИЮ
    user = await get_user_safe(request)
    
    if not user:
        return JsonResponse({'message': 'Ошибка: Нет пользователей в базе!'}, status=403)

    instrument_id = request.POST.get('id')
    
    # Запуск транзакции
    message = await process_booking_transaction(instrument_id, user)
    
    return JsonResponse({'message': message})

@sync_to_async
def process_booking_transaction(inst_id, user):
    try:
        with transaction.atomic():
            # ЯВНАЯ БЛОКИРОВКА СТРОКИ (SELECT ... FOR UPDATE)
            # Это защищает от двойного бронирования
            instrument = Instrument.objects.select_for_update().get(id=inst_id)
            
            if instrument.status != 'available':
                return "❌ Ошибка: Инструмент уже занят кем-то другим!"
            
            # Меняем статус
            instrument.status = 'rented'
            instrument.save()
            
            # Создаем запись
            Rental.objects.create(instrument=instrument, user=user)
            return "✅ Успешно! Вы забронировали инструмент."
            
    except Instrument.DoesNotExist:
        return "Ошибка: Инструмент не найден"

from django.contrib.auth.decorators import login_required

@login_required(login_url='/admin/')
def profile(request):
    # Показываем только аренды текущего пользователя
    my_rentals = Rental.objects.filter(user=request.user).select_related('instrument').order_by('-created_at')
    return render(request, 'profile.html', {'rentals': my_rentals})