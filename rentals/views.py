from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse
from django.db import transaction
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from asgiref.sync import sync_to_async
from .models import Instrument, Rental, Category, Brand, UserProfile
from .forms import UserRegistrationForm, ReviewForm
from django.core.serializers import serialize
import json

# --- 1. РЕГИСТРАЦИЯ ---
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            # Создаем профиль
            phone = form.cleaned_data.get('phone')
            address = form.cleaned_data.get('address')
            UserProfile.objects.create(user=user, phone_number=phone, address=address)
            
            login(request, user) # Сразу входим
            return redirect('catalog')
    else:
        form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form})

# --- 2. КАТАЛОГ (С новыми фильтрами) ---
def catalog(request):
    # Используем select_related для оптимизации (меньше запросов к БД)
    instruments = Instrument.objects.select_related('category', 'brand', 'location').all()
    
    # Фильтрация
    cat_id = request.GET.get('category')
    brand_id = request.GET.get('brand')
    
    if cat_id:
        instruments = instruments.filter(category_id=cat_id)
    if brand_id:
        instruments = instruments.filter(brand_id=brand_id)

    context = {
        'instruments': instruments,
        'categories': Category.objects.all(),
        'brands': Brand.objects.all(),
    }
    return render(request, 'catalog.html', context)

# --- 3. ЛИЧНЫЙ КАБИНЕТ ---
@login_required
def profile(request):
    rentals = Rental.objects.filter(user=request.user).select_related('instrument').order_by('-created_at')
    return render(request, 'profile.html', {'rentals': rentals})

# --- 4. REST API (Требование преподавателя) ---
def api_instruments(request):
    """
    Возвращает список инструментов в формате JSON.
    Это реализует требование 'REST API'.
    """
    instruments = Instrument.objects.all().values(
        'id', 'name', 'price_per_day', 'status', 
        'category__name', 'brand__name'
    )
    return JsonResponse({'results': list(instruments)}, safe=False)

# --- 5. АСИНХРОННОЕ БРОНИРОВАНИЕ ---
@sync_to_async
def get_user_safe(request):
    if request.user.is_authenticated:
        return request.user
    return None

async def create_booking_async(request):
    if request.method != 'POST':
        return JsonResponse({'error': 'Method not allowed'}, status=405)
    
    user = await get_user_safe(request)
    if not user:
         return JsonResponse({'message': 'Пожалуйста, войдите в систему!'}, status=403)

    instrument_id = request.POST.get('id')
    result_msg = await process_booking_transaction(instrument_id, user)
    
    # Возвращаем статус в зависимости от сообщения
    status_code = 200 if "Успешно" in result_msg else 400
    return JsonResponse({'message': result_msg}, status=status_code)

@sync_to_async
def process_booking_transaction(inst_id, user):
    try:
        with transaction.atomic():
            instrument = Instrument.objects.select_for_update().get(id=inst_id)
            
            if instrument.status != 'available':
                return "❌ Инструмент уже занят или на обслуживании!"
            
            instrument.status = 'rented'
            instrument.save()
            
            # В новой структуре start_date обязателен, ставим сегодня
            import datetime
            Rental.objects.create(
                instrument=instrument, 
                user=user,
                start_date=datetime.date.today()
            )
            return "✅ Успешно забронировано!"
            
    except Instrument.DoesNotExist:
        return "Ошибка: Инструмент не найден"
    
# --- 6. ОТМЕНА БРОНИРОВАНИЯ ---
@login_required
def cancel_rental(request, rental_id):
    # Ищем аренду, которая принадлежит текущему пользователю
    rental = get_object_or_404(Rental, id=rental_id, user=request.user, is_active=True)
    
    if request.method == 'POST':
        with transaction.atomic():
            # 1. Деактивируем аренду
            rental.is_active = False
            rental.save()
            
            # 2. Освобождаем инструмент
            instrument = rental.instrument
            instrument.status = 'available'
            instrument.save()
            
    return redirect('profile')

# --- 7. ДЕТАЛЬНАЯ СТРАНИЦА + ОТЗЫВЫ ---
def instrument_detail(request, pk):
    instrument = get_object_or_404(Instrument, pk=pk)
    reviews = instrument.reviews.select_related('user').all()
    
    # Обработка добавления отзыва
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        
        form = ReviewForm(request.POST)
        if form.is_valid():
            review = form.save(commit=False)
            review.instrument = instrument
            review.user = request.user
            review.save()
            return redirect('instrument_detail', pk=pk)
    else:
        form = ReviewForm()

    return render(request, 'instrument_detail.html', {
        'instrument': instrument,
        'reviews': reviews,
        'form': form
    })