from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# cСПРАВОЧНИКИ 

class Category(models.Model):
    name = models.CharField("Название категории", max_length=100)
    slug = models.SlugField(unique=True, help_text="URL-метка (например, guitars)")

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Категория"
        verbose_name_plural = "Категории"

class Brand(models.Model):
    name = models.CharField("Бренд", max_length=100)
    country = models.CharField("Страна", max_length=100, blank=True)

    def __str__(self):
        return self.name
    
    class Meta:
        verbose_name = "Бренд"
        verbose_name_plural = "Бренды"

class Location(models.Model):
    name = models.CharField("Название филиала", max_length=100)
    address = models.TextField("Адрес")
    phone = models.CharField("Телефон", max_length=20)

    def __str__(self):
        return f"{self.name} ({self.address})"
    
    class Meta:
        verbose_name = "Филиал"
        verbose_name_plural = "Филиалы"

# --- ПОЛЬЗОВАТЕЛИ ---

class UserProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='profile')
    phone_number = models.CharField("Телефон", max_length=20, blank=True)
    address = models.TextField("Адрес проживания", blank=True)
    avatar = models.ImageField("Аватар", upload_to='avatars/', blank=True, null=True)

    def __str__(self):
        return f"Профиль {self.user.username}"
    
    class Meta:
        verbose_name = "Профиль пользователя"
        verbose_name_plural = "Профили пользователей"

# --- ТОВАРЫ ---

class Instrument(models.Model):
    STATUS_CHOICES = [
        ('available', 'В наличии'),
        ('rented', 'В аренде'),
        ('maintenance', 'На обслуживании'),
    ]
    
    name = models.CharField("Название модели", max_length=100)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, verbose_name="Категория")
    brand = models.ForeignKey(Brand, on_delete=models.SET_NULL, null=True, verbose_name="Бренд")
    location = models.ForeignKey(Location, on_delete=models.SET_NULL, null=True, verbose_name="Где находится")
    
    description = models.TextField("Описание", blank=True)
    price_per_day = models.DecimalField("Цена за сутки", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='available')
    
    inventory_number = models.CharField("Инвентарный номер", max_length=50, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.brand} {self.name} ({self.inventory_number})"
    
    class Meta:
        verbose_name = "Инструмент"
        verbose_name_plural = "Инструменты"

class InstrumentPhoto(models.Model):
    instrument = models.ForeignKey(Instrument, related_name='photos', on_delete=models.CASCADE)
    image = models.ImageField("Фото", upload_to='instruments/')
    
    class Meta:
        verbose_name = "Фото инструмента"
        verbose_name_plural = "Фото инструментов"

# --- БИЗНЕС-ЛОГИКА ---

class Rental(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, verbose_name="Инструмент")
    user = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Клиент")
    start_date = models.DateField("Дата начала")
    end_date = models.DateField("Дата возврата", null=True, blank=True)
    total_price = models.DecimalField("Итоговая стоимость", max_digits=10, decimal_places=2, default=0)
    is_active = models.BooleanField("Активна", default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Аренда #{self.id} - {self.instrument.name}"
    
    class Meta:
        verbose_name = "Аренда"
        verbose_name_plural = "Аренды"

class Payment(models.Model):
    rental = models.ForeignKey(Rental, on_delete=models.CASCADE, related_name='payments')
    amount = models.DecimalField("Сумма", max_digits=10, decimal_places=2)
    payment_date = models.DateTimeField(auto_now_add=True)
    is_successful = models.BooleanField("Успешно", default=True)

    def __str__(self):
        return f"Платеж {self.amount} р. за аренду #{self.rental.id}"
    
    class Meta:
        verbose_name = "Платеж"
        verbose_name_plural = "Платежи"

class Maintenance(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    date = models.DateField("Дата обслуживания")
    description = models.TextField("Что сделано")
    cost = models.DecimalField("Стоимость ремонта", max_digits=10, decimal_places=2)

    def __str__(self):
        return f"Ремонт {self.instrument.name} от {self.date}"
    
    class Meta:
        verbose_name = "Техобслуживание"
        verbose_name_plural = "Журнал ТО"

class Review(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE, related_name='reviews')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    rating = models.IntegerField("Оценка", validators=[MinValueValidator(1), MaxValueValidator(5)])
    comment = models.TextField("Комментарий")
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Отзыв {self.user.username} на {self.instrument.name}"
    
    class Meta:
        verbose_name = "Отзыв"
        verbose_name_plural = "Отзывы"