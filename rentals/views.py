from django.shortcuts import render
from django.http import JsonResponse
from django.db import transaction
from asgiref.sync import sync_to_async
from .models import Instrument, Rental

# Отображение каталога
def catalog(request):
    instruments = Instrument.objects.all().order_by('id')
    return render(request, 'catalog.html', {'instruments': instruments})

# Асинхронное бронирование с защитой транзакции
async def create_booking_async(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    # Получаем пользователя (в рамках лабы считаем, что это админ, если не залогинен)
    user = await sync_to_async(lambda: request.user)()
    if not user.is_authenticated:
        # Пытаемся найти админа для теста, если не залогинен
        from django.contrib.auth.models import User
        try:
            user = await User.objects.afirst()
        except:
            return JsonResponse({'message': 'Создайте суперпользователя!'}, status=403)

    instrument_id = request.POST.get('id')
    
    # Запуск транзакции
    message = await process_booking_transaction(instrument_id, user)
    return JsonResponse({'message': message})

@sync_to_async
def process_booking_transaction(inst_id, user):
    try:
        with transaction.atomic():
            # ЯВНАЯ БЛОКИРОВКА СТРОКИ
            instrument = Instrument.objects.select_for_update().get(id=inst_id)
            
            if instrument.status != 'available':
                return "❌ Ошибка: Инструмент уже занят кем-то другим!"
            
            instrument.status = 'rented'
            instrument.save()
            
            Rental.objects.create(instrument=instrument, user=user)
            return "✅ Успешно! Вы забронировали инструмент."
            
    except Instrument.DoesNotExist:
        return "Ошибка: Инструмент не найден"