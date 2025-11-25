from django.db import models
from django.contrib.auth.models import User

class Instrument(models.Model):
    STATUS_CHOICES = [
        ('available', 'В наличии'),
        ('rented', 'В аренде'),
    ]
    name = models.CharField("Название", max_length=100)
    category = models.CharField("Категория", max_length=50)
    price = models.DecimalField("Цена за сутки", max_digits=10, decimal_places=2)
    status = models.CharField("Статус", max_length=20, choices=STATUS_CHOICES, default='available')

    def __str__(self):
        return self.name

class Rental(models.Model):
    instrument = models.ForeignKey(Instrument, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def __str__(self):
        return f"Аренда {self.instrument.name}"