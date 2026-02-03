
from django.db import models
from django.contrib.auth.models import User
from django.db.models.signals import post_save
from django.dispatch import receiver


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    bio = models.TextField(max_length=500, blank=True, verbose_name='Про себе')
    avatar = models.ImageField(upload_to='avatar/', blank=True, null=True, verbose_name='Аватар')
    birth_date = models.DateField(null=True, blank=True, verbose_name="Дата народження")
    location = models.CharField(max_length=50, blank=True, verbose_name='Місто')
    website = models.URLField(blank=True, verbose_name='Веб сайт')

    class Meta:
        verbose_name='Профіль'
        verbose_name_plural='Профілі'

    def __str__(self):
        return f"Профіль {self.user.username}"

