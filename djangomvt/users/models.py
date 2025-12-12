from django.db import models

# Create your models here.
class User(models.Model):
    username = models.CharField(max_length=150, unique=True, verbose_name="Ім'я користувача")
    first_name = models.CharField(max_length=30, verbose_name="Ім'я")
    last_name = models.CharField(max_length=30, verbose_name="Прізвище")
    email = models.EmailField(unique=True, verbose_name="Електронна пошта")
    password = models.CharField(max_length=128, verbose_name="Пароль")
    date_joined = models.DateTimeField(auto_now_add=True, verbose_name="Дата приєднання")
    is_active = models.BooleanField(default=True, verbose_name="Активний")
    image = models.ImageField(upload_to='images/', null=True, blank=True, verbose_name="Зображення користувача")
