# Гайд: CRUD для постів (Створення, Редагування, Видалення)

## Мета

Додати функціонал створення, редагування та видалення постів для зареєстрованих користувачів. Кожен користувач може редагувати та видаляти **тільки свої** пости.

## Що вже є в проекті

- Модель `Post` з полем `author = ForeignKey(User)` (`apps/main/models.py`)
- Модель `Category` з полем `slug` (`apps/main/models.py`)
- Views: `post_list`, `post_detail` (`apps/main/views.py`)
- Авторизація: login, register, profile, logout (`apps/accounts/`)
- `LOGIN_URL = 'accounts:login'` (`config/settings.py`)
- Tailwind CSS для стилізації

## Що потрібно додати

| Файл | Що додати |
|------|-----------|
| `apps/main/forms.py` | Форма `PostForm` (ModelForm) |
| `apps/main/views.py` | Views: `post_create`, `post_update`, `post_delete` |
| `apps/main/urls.py` | URL маршрути для CRUD |
| `templates/main/post_form.html` | Шаблон форми створення/редагування |
| `templates/main/post_confirm_delete.html` | Шаблон підтвердження видалення |
| `templates/main/post_details.html` | Кнопки "Редагувати" та "Видалити" |
| `templates/main/post_list.html` | Кнопка "Створити пост" |
| `templates/base.html` | Посилання "Створити пост" в навігації |

---

## Крок 1: Створення форми PostForm

**Файл:** `apps/main/forms.py`

Створіть новий файл `forms.py` в додатку `main`.

```python
from django import forms
from .models import Post


class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['category', 'title', 'slug', 'image', 'content']
        widgets = {
            'title': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                'placeholder': 'Введіть заголовок поста',
            }),
            'slug': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
                'placeholder': 'slug-поста (автоматично або вручну)',
            }),
            'category': forms.Select(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent',
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg file:mr-4 file:py-2 file:px-4 file:rounded-lg file:border-0 file:bg-teal-50 file:text-teal-700 hover:file:bg-teal-100',
            }),
            'content': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent resize-none',
                'rows': 10,
                'placeholder': 'Напишіть вміст поста...',
            }),
        }
        labels = {
            'title': 'Заголовок',
            'slug': 'Slug (URL)',
            'category': 'Категорія',
            'image': 'Зображення',
            'content': 'Контент',
        }
```

### Пояснення:

- **ModelForm** — автоматично створює поля на основі моделі `Post`
- **fields** — перелік полів, які користувач може заповнити (без `author`, `likes`, `views` — вони встановлюються автоматично)
- **widgets** — Tailwind CSS класи для стилізації полів
- **labels** — українські назви полів

---

## Крок 2: Створення Views

**Файл:** `apps/main/views.py`

Додайте нові імпорти та три нові view-функції.

### 2.1 Додайте імпорти

На початку файлу `views.py` додайте:

```python
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import PostForm
```

**Повний список імпортів після змін:**

```python
import os
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from .models import Post, Category
from .forms import PostForm
```

### 2.2 View: Створення поста

```python
@login_required
def post_create(request):
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES)
        if form.is_valid():
            post = form.save(commit=False)
            post.author = request.user
            post.save()
            return redirect(post.get_absolute_url())
    else:
        form = PostForm()
    
    return render(request, 'main/post_form.html', {
        'form': form,
        'title': 'Створити пост',
    })
```

### Пояснення:

- **`@login_required`** — тільки авторизовані користувачі можуть створювати пости. Якщо користувач не авторизований, його перенаправить на сторінку входу (`LOGIN_URL = 'accounts:login'`)
- **`request.FILES`** — обов'язково для завантаження зображень
- **`commit=False`** — зберігає форму без запису в БД, щоб спочатку додати автора
- **`post.author = request.user`** — автоматично встановлює поточного користувача як автора
- **`post.save()`** — зберігає пост у БД
- **`redirect(post.get_absolute_url())`** — перенаправляє на сторінку створеного поста

### 2.3 View: Редагування поста

```python
@login_required
def post_update(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    
    # Перевірка: тільки автор може редагувати свій пост
    if post.author != request.user:
        return HttpResponseForbidden("Ви не маєте права редагувати цей пост.")
    
    if request.method == 'POST':
        form = PostForm(request.POST, request.FILES, instance=post)
        if form.is_valid():
            form.save()
            return redirect(post.get_absolute_url())
    else:
        form = PostForm(instance=post)
    
    return render(request, 'main/post_form.html', {
        'form': form,
        'title': 'Редагувати пост',
        'post': post,
    })
```

### Пояснення:

- **`get_object_or_404(Post, id=id, slug=slug)`** — знаходить пост або повертає 404
- **`post.author != request.user`** — перевірка, що поточний користувач є автором поста
- **`HttpResponseForbidden`** — повертає помилку 403 (Заборонено), якщо користувач не є автором
- **`instance=post`** — заповнює форму даними існуючого поста
- При GET запиті — показує форму з поточними даними поста
- При POST запиті — зберігає зміни

### 2.4 View: Видалення поста

```python
@login_required
def post_delete(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    
    # Перевірка: тільки автор може видалити свій пост
    if post.author != request.user:
        return HttpResponseForbidden("Ви не маєте права видаляти цей пост.")
    
    if request.method == 'POST':
        post.delete()  # Сигнал автоматично видалить зображення
        return redirect('main:post_list')
    
    return render(request, 'main/post_confirm_delete.html', {
        'post': post,
    })
```

### Пояснення:

- **Перевірка автора** — аналогічно до редагування
- **`request.method == 'POST'`** — видалення відбувається тільки через POST запит (для безпеки). GET запит показує сторінку підтвердження
- **`post.delete()`** — видаляє пост з БД. Зображення видаляється автоматично через сигнал (див. Крок 2.5)
- **`redirect('main:post_list')`** — перенаправляє на список постів після видалення

### Чому видалення тільки через POST?

Видалення через GET запит небезпечне — бот або випадковий клік можуть видалити пост. POST запит вимагає підтвердження через форму з CSRF токеном.

---

## Крок 2.5: Автоматичне видалення зображень через сигнали

Замість ручного видалення зображення у view, можна використати **Django сигнали** для автоматичного видалення файлів при видаленні або оновленні моделі.

**Файл:** `apps/main/models.py`

Додайте в кінець файлу після визначення моделей:

```python
from django.db.models.signals import post_delete, pre_save
from django.dispatch import receiver
import os

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
```

### Пояснення:

- **`@receiver(post_delete, sender=Post)`** — сигнал спрацьовує після видалення поста
- **`delete_post_image`** — автоматично видаляє файл зображення з диска
- **`@receiver(pre_save, sender=Post)`** — сигнал спрацьовує перед збереженням поста
- **`delete_old_image_on_update`** — видаляє старе зображення, якщо користувач завантажує нове при редагуванні

### Переваги використання сигналів:

✅ Автоматичне видалення — не потрібно додавати код у кожну view  
✅ Видаляє старі зображення при оновленні поста  
✅ Працює навіть при видаленні через адмін-панель  
✅ Централізована логіка — весь код в одному місці  

---

## Крок 3: Налаштування URL

**Файл:** `apps/main/urls.py`

Додайте три нові маршрути:

```python
from django.urls import path
from . import views

app_name = "main"

urlpatterns = [
    path('', views.post_list, name="post_list"),
    path('category/<slug:category_slug>', views.post_list, name="post_list_by_category"),
    path('post/create/', views.post_create, name="post_create"),
    path('post/<int:id>/<slug:slug>', views.post_detail, name="post_detail"),
    path('post/<int:id>/<slug:slug>/edit/', views.post_update, name="post_update"),
    path('post/<int:id>/<slug:slug>/delete/', views.post_delete, name="post_delete"),
]
```

### Пояснення:

- **`post/create/`** — сторінка створення нового поста
- **`post/<int:id>/<slug:slug>/edit/`** — сторінка редагування поста
- **`post/<int:id>/<slug:slug>/delete/`** — сторінка підтвердження видалення

⚠️ **Важливо:** маршрут `post/create/` повинен бути **перед** `post/<int:id>/<slug:slug>`, інакше Django спробує інтерпретувати "create" як `<slug:slug>`.

---

## Крок 4: Створення шаблонів

### 4.1 Шаблон форми створення/редагування

**Файл:** `apps/main/templates/main/post_form.html`

```html
{% extends 'base.html' %}

{% block title %}{{ title }}{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto">
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="bg-gradient-to-r from-teal-600 to-teal-700 text-white px-8 py-6">
            <h1 class="text-3xl font-bold">{{ title }}</h1>
        </div>
        <div class="p-8">
            <form method="post" enctype="multipart/form-data" novalidate>
                {% csrf_token %}
                
                {% for field in form %}
                <div class="mb-5">
                    <label for="{{ field.id_for_label }}" class="block text-sm font-semibold text-gray-700 mb-2">
                        {{ field.label }}
                        {% if field.field.required %}
                            <span class="text-red-500">*</span>
                        {% endif %}
                    </label>
                    {{ field }}
                    {% if field.errors %}
                        {% for error in field.errors %}
                            <p class="mt-2 text-sm text-red-600">{{ error }}</p>
                        {% endfor %}
                    {% endif %}
                    {% if field.help_text %}
                        <p class="mt-1 text-xs text-gray-500">{{ field.help_text }}</p>
                    {% endif %}
                </div>
                {% endfor %}

                {% if form.errors and not form.fields %}
                    <div class="mb-4 p-4 bg-red-100 border border-red-400 text-red-800 rounded-lg">
                        {{ form.non_field_errors }}
                    </div>
                {% endif %}

                <div class="flex gap-4 mt-6">
                    <button type="submit" class="bg-teal-600 hover:bg-teal-700 text-white font-bold py-3 px-8 rounded-lg transition duration-200 transform hover:scale-[1.02] shadow-lg">
                        {% if post %}
                            Зберегти зміни
                        {% else %}
                            Створити пост
                        {% endif %}
                    </button>
                    <a href="{% if post %}{{ post.get_absolute_url }}{% else %}{% url 'main:post_list' %}{% endif %}" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-3 px-8 rounded-lg transition duration-200">
                        Скасувати
                    </a>
                </div>
            </form>
        </div>
    </div>
</div>
{% endblock %}
```

### Пояснення:

- **`enctype="multipart/form-data"`** — обов'язково для завантаження файлів (зображень)
- **`{% csrf_token %}`** — захист від CSRF атак
- **Цикл `{% for field in form %}`** — виводить всі поля форми автоматично
- **`field.errors`** — виводить помилки валідації для кожного поля
- **`{% if post %}`** — визначає, чи це створення чи редагування (змінює текст кнопки)
- **Кнопка "Скасувати"** — повертає на сторінку поста або на список постів

### 4.2 Шаблон підтвердження видалення

**Файл:** `apps/main/templates/main/post_confirm_delete.html`

```html
{% extends 'base.html' %}

{% block title %}Видалити пост{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto">
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="bg-red-600 text-white px-8 py-6">
            <h1 class="text-3xl font-bold">Видалити пост</h1>
        </div>
        <div class="p-8 text-center">
            <div class="mb-6">
                <svg class="mx-auto h-16 w-16 text-red-500" fill="none" viewBox="0 0 24 24" stroke="currentColor">
                    <path stroke-linecap="round" stroke-linejoin="round" stroke-width="2" d="M12 9v2m0 4h.01m-6.938 4h13.856c1.54 0 2.502-1.667 1.732-2.5L13.732 4c-.77-.833-1.964-.833-2.732 0L4.082 16.5c-.77.833.192 2.5 1.732 2.5z" />
                </svg>
            </div>
            <h2 class="text-2xl font-bold text-gray-800 mb-4">Ви впевнені?</h2>
            <p class="text-gray-600 mb-2">Ви збираєтесь видалити пост:</p>
            <p class="text-xl font-semibold text-gray-800 mb-6">"{{ post.title }}"</p>
            <p class="text-red-600 text-sm mb-8">Цю дію неможливо скасувати!</p>
            
            <div class="flex gap-4 justify-center">
                <form method="post">
                    {% csrf_token %}
                    <button type="submit" class="bg-red-600 hover:bg-red-700 text-white font-bold py-3 px-8 rounded-lg transition duration-200 transform hover:scale-[1.02] shadow-lg">
                        Так, видалити
                    </button>
                </form>
                <a href="{{ post.get_absolute_url }}" class="bg-gray-200 hover:bg-gray-300 text-gray-700 font-bold py-3 px-8 rounded-lg transition duration-200">
                    Скасувати
                </a>
            </div>
        </div>
    </div>
</div>
{% endblock %}
```

### Пояснення:

- **SVG іконка** — попереджувальний трикутник
- **Форма з POST** — видалення відбувається тільки через POST запит
- **`{% csrf_token %}`** — захист від CSRF
- **Кнопка "Скасувати"** — повертає на сторінку поста

---

## Крок 5: Додати кнопки в існуючі шаблони

### 5.1 Кнопки "Редагувати" та "Видалити" на сторінці поста

**Файл:** `apps/main/templates/main/post_details.html`

Знайдіть блок з датою оновлення та кнопкою "Повернутися до списку" (приблизно рядки 35-38):

```html
<div class="p-8 pt-6 border-t border-gray-200 flex items-center justify-between">
    <p class="text-sm text-gray-500">Оновлено: {{ post.updated_at|date:"d.m.Y H:i" }}</p>
    <a href="{% url 'main:post_list' %}" class="inline-flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors font-medium">← Повернутися до списку</a>
</div>
```

**Замініть на:**

```html
<div class="p-8 pt-6 border-t border-gray-200">
    <div class="flex items-center justify-between">
        <p class="text-sm text-gray-500">Оновлено: {{ post.updated_at|date:"d.m.Y H:i" }}</p>
        <div class="flex items-center gap-3">
            {% if user.is_authenticated and user == post.author %}
                <a href="{% url 'main:post_update' post.id post.slug %}" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg transition-colors font-medium">
                    ✏️ Редагувати
                </a>
                <a href="{% url 'main:post_delete' post.id post.slug %}" class="inline-flex items-center gap-2 bg-red-500 hover:bg-red-600 text-white px-4 py-2 rounded-lg transition-colors font-medium">
                    🗑️ Видалити
                </a>
            {% endif %}
            <a href="{% url 'main:post_list' %}" class="inline-flex items-center gap-2 bg-gray-100 hover:bg-gray-200 text-gray-700 px-4 py-2 rounded-lg transition-colors font-medium">
                ← Повернутися до списку
            </a>
        </div>
    </div>
</div>
```

### Пояснення:

- **`{% if user.is_authenticated and user == post.author %}`** — кнопки "Редагувати" та "Видалити" видно **тільки автору** поста
- Інші користувачі та гості бачать тільки кнопку "Повернутися до списку"

### 5.2 Кнопка "Створити пост" на сторінці списку

**Файл:** `apps/main/templates/main/post_list.html`

Знайдіть заголовок сторінки (рядок 8):

```html
<h1 class="text-4xl font-bold text-gray-800 mb-4">{% if category %}{{ category.name }}{% else %}Всі пости{% endif %}</h1>
```

**Замініть на:**

```html
<div class="flex items-center justify-between mb-4">
    <h1 class="text-4xl font-bold text-gray-800">{% if category %}{{ category.name }}{% else %}Всі пости{% endif %}</h1>
    {% if user.is_authenticated %}
        <a href="{% url 'main:post_create' %}" class="inline-flex items-center gap-2 bg-teal-600 hover:bg-teal-700 text-white px-6 py-3 rounded-lg transition-colors font-medium shadow-lg hover:shadow-xl transform hover:scale-[1.02] transition duration-200">
            ➕ Створити пост
        </a>
    {% endif %}
</div>
```

### Пояснення:

- **`{% if user.is_authenticated %}`** — кнопка "Створити пост" видна тільки авторизованим користувачам
- Гості не бачать цю кнопку

### 5.3 Посилання в навігації (опціонально)

**Файл:** `apps/main/templates/base.html`

Знайдіть блок навігації з посиланнями (рядки 18-33) і додайте посилання "Створити пост" поруч з іншими:

Після рядка з "Профіль":

```html
<a href="{% url 'accounts:profile' %}" class="text-gray-700 hover:text-teal-600 transition-colors">Профіль</a>
```

Додайте:

```html
<a href="{% url 'main:post_create' %}" class="bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg transition-colors">Створити пост</a>
```

---

## Крок 6: Автоматична генерація slug (опціонально)

Якщо ви хочете, щоб slug генерувався автоматично з заголовка, додайте JavaScript у шаблон форми або перевизначте метод `save()` у формі.

### Варіант 1: JavaScript у шаблоні

Додайте в кінець `post_form.html` перед `{% endblock %}`:

```html
<script>
    const titleInput = document.getElementById('id_title');
    const slugInput = document.getElementById('id_slug');
    
    if (titleInput && slugInput) {
        titleInput.addEventListener('input', function() {
            // Транслітерація не включена — slug потрібно вводити латиницею
            slugInput.value = this.value
                .toLowerCase()
                .replace(/[^a-z0-9\s-]/g, '')
                .replace(/\s+/g, '-')
                .replace(/-+/g, '-')
                .trim();
        });
    }
</script>
```

### Варіант 2: Автогенерація в моделі

Додайте метод `save()` у модель `Post` (`apps/main/models.py`):

```python
from django.utils.text import slugify
import uuid

class Post(models.Model):
    # ... існуючі поля ...
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            if not base_slug:
                base_slug = str(uuid.uuid4())[:8]
            # Перевірка унікальності
            slug = base_slug
            counter = 1
            while Post.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)
```

Якщо використовуєте автогенерацію, можна зробити поле `slug` необов'язковим у формі:

```python
class PostForm(forms.ModelForm):
    class Meta:
        model = Post
        fields = ['category', 'title', 'slug', 'image', 'content']
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['slug'].required = False
```

---

## Схема роботи доступу

```
Гість (не авторизований):
├── ✅ Переглядати список постів
├── ✅ Переглядати окремий пост
├── ❌ Створювати пости → перенаправлення на сторінку входу
├── ❌ Редагувати пости → перенаправлення на сторінку входу
└── ❌ Видаляти пости → перенаправлення на сторінку входу

Авторизований користувач:
├── ✅ Переглядати список постів
├── ✅ Переглядати окремий пост
├── ✅ Створювати нові пости
├── ✅ Редагувати СВОЇ пости
├── ✅ Видаляти СВОЇ пости
├── ❌ Редагувати ЧУЖІ пости → помилка 403 (Заборонено)
└── ❌ Видаляти ЧУЖІ пости → помилка 403 (Заборонено)
```

---

## Механізми захисту

### 1. `@login_required`

Декоратор, який перевіряє, чи авторизований користувач. Якщо ні — перенаправляє на `LOGIN_URL`.

```python
@login_required
def post_create(request):
    # Ця функція доступна тільки авторизованим користувачам
    ...
```

### 2. Перевірка автора

Ручна перевірка, що поточний користувач є автором поста:

```python
if post.author != request.user:
    return HttpResponseForbidden("Ви не маєте права редагувати цей пост.")
```

### 3. Перевірка в шаблонах

Кнопки "Редагувати" та "Видалити" показуються тільки автору:

```html
{% if user.is_authenticated and user == post.author %}
    <!-- кнопки редагування та видалення -->
{% endif %}
```

⚠️ **Важливо:** перевірка в шаблонах — це лише **візуальне** приховування. Основний захист — у views (декоратор + перевірка автора). Навіть якщо хтось знає URL, він не зможе редагувати/видалити чужий пост.

### 4. CSRF захист

Всі форми містять `{% csrf_token %}` для захисту від Cross-Site Request Forgery атак.

### 5. Видалення тільки через POST

Видалення відбувається тільки через POST запит з підтвердженням, а не через GET.

---

## Тестування

### 1. Створення поста

1. Авторизуйтесь на сайті
2. Натисніть "Створити пост"
3. Заповніть форму (заголовок, slug, категорія, контент)
4. Натисніть "Створити пост"
5. ✅ Ви повинні бути перенаправлені на сторінку нового поста
6. ✅ Автором поста повинен бути ваш username

### 2. Редагування поста

1. Відкрийте свій пост
2. Натисніть "Редагувати"
3. Змініть заголовок або контент
4. Натисніть "Зберегти зміни"
5. ✅ Зміни повинні зберегтися

### 3. Видалення поста

1. Відкрийте свій пост
2. Натисніть "Видалити"
3. Підтвердіть видалення
4. ✅ Пост повинен бути видалений, ви перенаправлені на список постів

### 4. Перевірка доступу

1. Авторизуйтесь як інший користувач
2. Відкрийте чужий пост
3. ✅ Кнопки "Редагувати" та "Видалити" не повинні відображатися
4. Спробуйте перейти за URL `/post/1/some-slug/edit/` для чужого поста
5. ✅ Повинна з'явитися помилка 403

### 5. Перевірка для гостя

1. Вийдіть з акаунту
2. Спробуйте перейти за URL `/post/create/`
3. ✅ Ви повинні бути перенаправлені на сторінку входу

---

## Поширені помилки

### 1. Помилка "The view didn't return an HttpResponse"

**Причина:** Функція view не повертає відповідь у всіх випадках.

**Рішення:** Переконайтесь, що `return render(...)` знаходиться **поза** блоком `if/else`, щоб функція завжди повертала відповідь.

### 2. Зображення не завантажується

**Причина:** Відсутній `enctype="multipart/form-data"` у тезі `<form>`.

**Рішення:** Додайте атрибут:
```html
<form method="post" enctype="multipart/form-data">
```

І не забудьте `request.FILES` у view:
```python
form = PostForm(request.POST, request.FILES)
```

### 3. Slug повинен бути унікальним

**Причина:** Два пости з однаковим slug.

**Рішення:** Використовуйте автогенерацію slug з перевіркою унікальності (див. Крок 6).

### 4. Маршрут `post/create/` не працює

**Причина:** Маршрут `post/<int:id>/<slug:slug>` перехоплює URL раніше.

**Рішення:** Розмістіть `post/create/` **перед** `post/<int:id>/<slug:slug>` у `urls.py`.

### 5. Помилка 403 при редагуванні свого поста

**Причина:** Автор поста не збігається з поточним користувачем.

**Рішення:** Перевірте, що при створенні поста ви правильно встановлюєте автора:
```python
post.author = request.user
```

---

## Корисні посилання

- [Django Forms](https://docs.djangoproject.com/en/stable/topics/forms/)
- [Django ModelForm](https://docs.djangoproject.com/en/stable/topics/forms/modelforms/)
- [Django login_required](https://docs.djangoproject.com/en/stable/topics/auth/default/#the-login-required-decorator)
- [Django File Uploads](https://docs.djangoproject.com/en/stable/topics/http/file-uploads/)
- [Django CSRF Protection](https://docs.djangoproject.com/en/stable/ref/csrf/)
