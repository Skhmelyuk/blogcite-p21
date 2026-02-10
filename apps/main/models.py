from django.db import models
from django.contrib.auth.models import User
from django.urls import reverse
import os
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver


class Category(models.Model):
  name = models.CharField(max_length=50, db_index=True, verbose_name="Ім'я категорії")
  slug = models.SlugField(max_length=50, unique=True, verbose_name="Слаг")

  class Meta:
      ordering = ["name"]
      verbose_name = "Категорія"
      verbose_name_plural = "Категорії"

  def __str__(self):
      return self.name
  
  def get_absolute_url(self):
      return reverse("main:post_list_by_category", args=[self.slug])

class Post(models.Model):
  category = models.ForeignKey(Category, on_delete=models.CASCADE, verbose_name="Категорія", null=True, blank=True)
  title = models.CharField(max_length=100, db_index=True, verbose_name="Заголовок")
  slug = models.SlugField(max_length=100, unique=True, verbose_name="Слаг")
  image = models.ImageField(upload_to="posts/%Y/%m/%d/", blank=True, verbose_name="Зображення")
  content = models.TextField(verbose_name="Контент")
  created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
  updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")
  likes = models.IntegerField(default=0, verbose_name="Лайки")
  views = models.IntegerField(default=0, verbose_name="Перегляди")
  author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")

  class Meta:
      ordering = ["-created_at"]
      verbose_name = "Пост"
      verbose_name_plural = "Пости"

  def __str__(self):
      return f" {self.title} - { self.created_at }"
  
  def get_absolute_url(self):
      return reverse("main:post_detail", args=[self.id, self.slug])

@receiver(post_delete, sender=Post)
def delete_post_image(sender, instance, **kwargs):
    """Видаляє файл зображення при видаленні поста"""
    if instance.image:
        if os.path.isfile(instance.image.path):
            os.remove(instance.image.path)

@receiver(pre_save, sender=Post)
def delete_old_image_on_update(sender, instance, **kwargs):
    """Видаляє старе зображення при оновленні поста новим зображенням"""
    if not instance.pk:
        return False
    
    try:
        old_image = Post.objects.get(pk=instance.pk).image
    except Post.DoesNotExist:
        return False
    
    new_image = instance.image
    if old_image and old_image != new_image:
        if os.path.isfile(old_image.path):
            os.remove(old_image.path)