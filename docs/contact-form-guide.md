# Гайд по створенню контактної форми в Django

## Зміст
1. [Вступ](#вступ)
2. [Створення додатку](#створення-додатку)
3. [Створення моделі](#створення-моделі)
4. [Створення форми](#створення-форми)
5. [Створення представлення (View)](#створення-представлення-view)
6. [Налаштування URL](#налаштування-url)
7. [Створення шаблону](#створення-шаблону)
8. [Налаштування email](#налаштування-email)
9. [Додаткові можливості](#додаткові-можливості)

---

## Вступ

Контактна форма - це важливий елемент будь-якого веб-сайту, що дозволяє відвідувачам зв'язатися з адміністрацією або власниками сайту. У цьому гайді ми створимо повнофункціональну контактну форму для Django проекту.

**Що ми реалізуємо:**
- Форма з полями: ім'я, email, тема, повідомлення
- Валідація даних
- Збереження повідомлень у базі даних
- Відправка email-повідомлень
- Захист від спаму (CSRF)
- Адмін-панель для перегляду повідомлень

---

## Створення додатку

### Крок 1: Створіть новий додаток

```bash
python manage.py startapp contact
```

### Крок 2: Додайте додаток до `INSTALLED_APPS`

У файлі `config/settings.py`:

```python
INSTALLED_APPS = [
    'django.contrib.admin',
    'django.contrib.auth',
    'django.contrib.contenttypes',
    'django.contrib.sessions',
    'django.contrib.messages',
    'django.contrib.staticfiles',
    'apps.main',
    'apps.cart',
    'apps.accounts',
    'apps.contact',  # Додайте цей рядок
]
```

---

## Створення моделі

### Файл: `apps/contact/models.py`

```python
from django.db import models
from django.utils import timezone


class ContactMessage(models.Model):
    """Модель для збереження повідомлень з контактної форми"""
    
    STATUS_CHOICES = [
        ('new', 'Нове'),
        ('in_progress', 'В обробці'),
        ('resolved', 'Вирішено'),
        ('closed', 'Закрито'),
    ]
    
    name = models.CharField(
        max_length=100,
        verbose_name='Ім\'я'
    )
    email = models.EmailField(
        verbose_name='Email'
    )
    subject = models.CharField(
        max_length=200,
        verbose_name='Тема'
    )
    message = models.TextField(
        verbose_name='Повідомлення'
    )
    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='new',
        verbose_name='Статус'
    )
    created_at = models.DateTimeField(
        default=timezone.now,
        verbose_name='Дата створення'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='Дата оновлення'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='Прочитано'
    )
    admin_notes = models.TextField(
        blank=True,
        null=True,
        verbose_name='Примітки адміністратора'
    )
    
    class Meta:
        verbose_name = 'Повідомлення'
        verbose_name_plural = 'Повідомлення'
        ordering = ['-created_at']
        
    def __str__(self):
        return f"{self.name} - {self.subject}"
    
    def mark_as_read(self):
        """Позначити повідомлення як прочитане"""
        self.is_read = True
        self.save()
```

### Створіть міграції

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## Створення форми

### Файл: `apps/contact/forms.py`

```python
from django import forms
from .models import ContactMessage


class ContactForm(forms.ModelForm):
    """Форма для контактних повідомлень"""
    
    class Meta:
        model = ContactMessage
        fields = ['name', 'email', 'subject', 'message']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ваше ім\'я',
                'required': True,
            }),
            'email': forms.EmailInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ваш email',
                'required': True,
            }),
            'subject': forms.TextInput(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Тема повідомлення',
                'required': True,
            }),
            'message': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
                'placeholder': 'Ваше повідомлення',
                'rows': 5,
                'required': True,
            }),
        }
    
    def clean_message(self):
        """Валідація поля повідомлення"""
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError(
                'Повідомлення повинно містити щонайменше 10 символів.'
            )
        return message
    
    def clean_name(self):
        """Валідація поля імені"""
        name = self.cleaned_data.get('name')
        if len(name) < 2:
            raise forms.ValidationError(
                'Ім\'я повинно містити щонайменше 2 символи.'
            )
        return name


class SimpleContactForm(forms.Form):
    """Альтернативна проста форма без моделі"""
    
    name = forms.CharField(
        max_length=100,
        label='Ім\'я',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ваше ім\'я',
        })
    )
    email = forms.EmailField(
        label='Email',
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ваш email',
        })
    )
    subject = forms.CharField(
        max_length=200,
        label='Тема',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Тема повідомлення',
        })
    )
    message = forms.CharField(
        label='Повідомлення',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Ваше повідомлення',
            'rows': 5,
        })
    )
```

---

## Створення представлення (View)

### Файл: `apps/contact/views.py`

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.views.generic import CreateView, ListView
from django.urls import reverse_lazy
from django.contrib.auth.mixins import LoginRequiredMixin
from .forms import ContactForm
from .models import ContactMessage


def contact_view(self, request):
    """Function-based view для контактної форми"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Зберігаємо повідомлення в базі даних
            contact_message = form.save()
            
            # Відправляємо email
            try:
                send_mail(
                    subject=f"Нове повідомлення: {contact_message.subject}",
                    message=f"Від: {contact_message.name} ({contact_message.email})\n\n{contact_message.message}",
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    'Дякуємо! Ваше повідомлення успішно відправлено.'
                )
            except BadHeaderError:
                messages.error(
                    request,
                    'Виявлено некоректний заголовок.'
                )
            except Exception as e:
                messages.warning(
                    request,
                    'Повідомлення збережено, але не вдалося відправити email.'
                )
            
            return redirect('contact:success')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact_form.html', {'form': form})


class ContactCreateView(CreateView):
    """Class-based view для контактної форми"""
    model = ContactMessage
    form_class = ContactForm
    template_name = 'contact/contact_form.html'
    success_url = reverse_lazy('contact:success')
    
    def form_valid(self, form):
        """Обробка валідної форми"""
        response = super().form_valid(form)
        
        # Відправка email
        try:
            send_mail(
                subject=f"Нове повідомлення: {self.object.subject}",
                message=f"Від: {self.object.name} ({self.object.email})\n\n{self.object.message}",
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(
                self.request,
                'Дякуємо! Ваше повідомлення успішно відправлено.'
            )
        except Exception as e:
            messages.warning(
                self.request,
                'Повідомлення збережено, але не вдалося відправити email.'
            )
        
        return response
    
    def form_invalid(self, form):
        """Обробка невалідної форми"""
        messages.error(
            self.request,
            'Будь ласка, виправте помилки у формі.'
        )
        return super().form_invalid(form)


class ContactMessageListView(LoginRequiredMixin, ListView):
    """Список повідомлень для адміністраторів"""
    model = ContactMessage
    template_name = 'contact/message_list.html'
    context_object_name = 'messages'
    paginate_by = 20
    
    def get_queryset(self):
        """Фільтрація повідомлень"""
        queryset = super().get_queryset()
        status = self.request.GET.get('status')
        if status:
            queryset = queryset.filter(status=status)
        return queryset


def contact_success_view(request):
    """Сторінка успішної відправки"""
    return render(request, 'contact/success.html')
```

---

## Налаштування URL

### Файл: `apps/contact/urls.py`

```python
from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    path('', views.ContactCreateView.as_view(), name='contact'),
    path('success/', views.contact_success_view, name='success'),
    path('messages/', views.ContactMessageListView.as_view(), name='message_list'),
]
```

### Додайте до головного `config/urls.py`:

```python
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('apps.main.urls')),
    path('cart/', include('apps.cart.urls')),
    path('accounts/', include('apps.accounts.urls')),
    path('contact/', include('apps.contact.urls')),  # Додайте цей рядок
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Створення шаблону

### Файл: `apps/contact/templates/contact/contact_form.html`

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Зв'язатися з нами{% endblock %}

{% block content %}
<div class="max-w-4xl mx-auto px-4 py-12">
    <div class="bg-white rounded-lg shadow-lg overflow-hidden">
        <div class="bg-blue-600 text-white px-6 py-4">
            <h2 class="text-2xl font-bold">Зв'язатися з нами</h2>
        </div>
        <div class="p-6">
            {% if messages %}
                {% for message in messages %}
                    <div class="mb-4 p-4 rounded-lg {% if message.tags == 'success' %}bg-green-100 text-green-800{% elif message.tags == 'error' %}bg-red-100 text-red-800{% else %}bg-blue-100 text-blue-800{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}

            <p class="text-gray-600 mb-6">
                Маєте питання або пропозиції? Заповніть форму нижче, і ми зв'яжемося з вами найближчим часом.
            </p>

            <form method="post" novalidate>
                {% csrf_token %}
                
                <div class="mb-4">
                    <label for="{{ form.name.id_for_label }}" class="block text-sm font-medium text-gray-700 mb-2">
                        {{ form.name.label }} <span class="text-red-500">*</span>
                    </label>
                    {{ form.name }}
                    {% if form.name.errors %}
                        <p class="mt-1 text-sm text-red-600">
                            {{ form.name.errors.0 }}
                        </p>
                    {% endif %}
                </div>

                <div class="mb-4">
                    <label for="{{ form.email.id_for_label }}" class="block text-sm font-medium text-gray-700 mb-2">
                        {{ form.email.label }} <span class="text-red-500">*</span>
                    </label>
                    {{ form.email }}
                    {% if form.email.errors %}
                        <p class="mt-1 text-sm text-red-600">
                            {{ form.email.errors.0 }}
                        </p>
                    {% endif %}
                </div>

                <div class="mb-4">
                    <label for="{{ form.subject.id_for_label }}" class="block text-sm font-medium text-gray-700 mb-2">
                        {{ form.subject.label }} <span class="text-red-500">*</span>
                    </label>
                    {{ form.subject }}
                    {% if form.subject.errors %}
                        <p class="mt-1 text-sm text-red-600">
                            {{ form.subject.errors.0 }}
                        </p>
                    {% endif %}
                </div>

                <div class="mb-6">
                    <label for="{{ form.message.id_for_label }}" class="block text-sm font-medium text-gray-700 mb-2">
                        {{ form.message.label }} <span class="text-red-500">*</span>
                    </label>
                    {{ form.message }}
                    {% if form.message.errors %}
                        <p class="mt-1 text-sm text-red-600">
                            {{ form.message.errors.0 }}
                        </p>
                    {% endif %}
                </div>

                <button type="submit" class="w-full bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-6 rounded-lg transition duration-200">
                    <i class="fas fa-paper-plane mr-2"></i>Відправити повідомлення
                </button>
            </form>
        </div>
    </div>

    <div class="mt-8 grid grid-cols-1 md:grid-cols-3 gap-6">
        <div class="bg-white rounded-lg shadow-md p-6 text-center">
            <i class="fas fa-envelope text-4xl text-blue-600 mb-3"></i>
            <h5 class="text-lg font-semibold mb-2">Email</h5>
            <p class="text-gray-600">info@example.com</p>
        </div>
        <div class="bg-white rounded-lg shadow-md p-6 text-center">
            <i class="fas fa-phone text-4xl text-blue-600 mb-3"></i>
            <h5 class="text-lg font-semibold mb-2">Телефон</h5>
            <p class="text-gray-600">+380 XX XXX XX XX</p>
        </div>
        <div class="bg-white rounded-lg shadow-md p-6 text-center">
            <i class="fas fa-map-marker-alt text-4xl text-blue-600 mb-3"></i>
            <h5 class="text-lg font-semibold mb-2">Адреса</h5>
            <p class="text-gray-600">Київ, Україна</p>
        </div>
    </div>
</div>
{% endblock %}
```

### Файл: `apps/contact/templates/contact/success.html`

```html
{% extends 'base.html' %}

{% block title %}Повідомлення відправлено{% endblock %}

{% block content %}
<div class="max-w-2xl mx-auto px-4 py-12">
    <div class="bg-white rounded-lg shadow-lg p-12 text-center">
        <i class="fas fa-check-circle text-7xl text-green-500 mb-6"></i>
        <h2 class="text-3xl font-bold text-gray-800 mb-4">Дякуємо!</h2>
        <p class="text-lg text-gray-600 mb-8">
            Ваше повідомлення успішно відправлено. Ми зв'яжемося з вами найближчим часом.
        </p>
        <a href="{% url 'main:post_list' %}" class="inline-block bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200">
            <i class="fas fa-home mr-2"></i>Повернутися на головну
        </a>
    </div>
</div>
{% endblock %}
```

### Файл: `apps/contact/templates/contact/message_list.html`

```html
{% extends 'base.html' %}

{% block title %}Повідомлення{% endblock %}

{% block content %}
<div class="max-w-7xl mx-auto px-4 py-8">
    <h2 class="text-3xl font-bold text-gray-800 mb-6">Повідомлення від користувачів</h2>
    
    <div class="mb-6">
        <form method="get" class="flex gap-3">
            <select name="status" class="px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent">
                <option value="">Всі статуси</option>
                <option value="new">Нові</option>
                <option value="in_progress">В обробці</option>
                <option value="resolved">Вирішені</option>
                <option value="closed">Закриті</option>
            </select>
            <button type="submit" class="px-6 py-2 bg-blue-600 hover:bg-blue-700 text-white font-semibold rounded-lg transition duration-200">
                Фільтрувати
            </button>
        </form>
    </div>

    <div class="bg-white rounded-lg shadow-md overflow-hidden">
        <div class="overflow-x-auto">
            <table class="min-w-full divide-y divide-gray-200">
                <thead class="bg-gray-50">
                    <tr>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Дата</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Ім'я</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Email</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Тема</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Статус</th>
                        <th class="px-6 py-3 text-left text-xs font-medium text-gray-500 uppercase tracking-wider">Прочитано</th>
                    </tr>
                </thead>
                <tbody class="bg-white divide-y divide-gray-200">
                    {% for message in messages %}
                    <tr class="hover:bg-gray-50">
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ message.created_at|date:"d.m.Y H:i" }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ message.name }}</td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm text-gray-900">{{ message.email }}</td>
                        <td class="px-6 py-4 text-sm text-gray-900">{{ message.subject }}</td>
                        <td class="px-6 py-4 whitespace-nowrap">
                            <span class="px-2 py-1 inline-flex text-xs leading-5 font-semibold rounded-full {% if message.status == 'new' %}bg-blue-100 text-blue-800{% elif message.status == 'in_progress' %}bg-yellow-100 text-yellow-800{% elif message.status == 'resolved' %}bg-green-100 text-green-800{% else %}bg-gray-100 text-gray-800{% endif %}">
                                {{ message.get_status_display }}
                            </span>
                        </td>
                        <td class="px-6 py-4 whitespace-nowrap text-sm">
                            {% if message.is_read %}
                                <i class="fas fa-check text-green-500"></i>
                            {% else %}
                                <i class="fas fa-times text-red-500"></i>
                            {% endif %}
                        </td>
                    </tr>
                    {% empty %}
                    <tr>
                        <td colspan="6" class="px-6 py-4 text-center text-gray-500">Повідомлень немає</td>
                    </tr>
                    {% endfor %}
                </tbody>
            </table>
        </div>
    </div>

    {% if is_paginated %}
    <div class="mt-6">
        <div class="flex justify-center items-center space-x-2">
            {% if page_obj.has_previous %}
            <a href="?page={{ page_obj.previous_page_number }}" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700">
                Попередня
            </a>
            {% endif %}
            
            <span class="px-4 py-2 bg-blue-600 text-white rounded-lg">
                {{ page_obj.number }} з {{ page_obj.paginator.num_pages }}
            </span>
            
            {% if page_obj.has_next %}
            <a href="?page={{ page_obj.next_page_number }}" class="px-4 py-2 bg-white border border-gray-300 rounded-lg hover:bg-gray-50 text-gray-700">
                Наступна
            </a>
            {% endif %}
        </div>
    </div>
    {% endif %}
</div>
{% endblock %}
```

---

## Налаштування email

### У файлі `config/settings.py` додайте:

```python
# Email налаштування
EMAIL_BACKEND = 'django.core.mail.backends.smtp.EmailBackend'
EMAIL_HOST = config('EMAIL_HOST', default='smtp.gmail.com')
EMAIL_PORT = config('EMAIL_PORT', default=587, cast=int)
EMAIL_USE_TLS = config('EMAIL_USE_TLS', default=True, cast=bool)
EMAIL_HOST_USER = config('EMAIL_HOST_USER', default='')
EMAIL_HOST_PASSWORD = config('EMAIL_HOST_PASSWORD', default='')
DEFAULT_FROM_EMAIL = config('DEFAULT_FROM_EMAIL', default='noreply@example.com')
CONTACT_EMAIL = config('CONTACT_EMAIL', default='admin@example.com')
```

### У файлі `.env` додайте:

```env
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@example.com
CONTACT_EMAIL=admin@example.com
```

### Для розробки (без реального email):

```python
# У settings.py для розробки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

---

## Додаткові можливості

### 1. Адмін-панель

#### Файл: `apps/contact/admin.py`

```python
from django.contrib import admin
from .models import ContactMessage


@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ['name', 'email', 'subject', 'status', 'is_read', 'created_at']
    list_filter = ['status', 'is_read', 'created_at']
    search_fields = ['name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['status', 'is_read']
    date_hierarchy = 'created_at'
    
    fieldsets = (
        ('Інформація про відправника', {
            'fields': ('name', 'email')
        }),
        ('Повідомлення', {
            'fields': ('subject', 'message')
        }),
        ('Статус', {
            'fields': ('status', 'is_read', 'admin_notes')
        }),
        ('Дати', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['mark_as_read', 'mark_as_resolved']
    
    def mark_as_read(self, request, queryset):
        """Позначити як прочитане"""
        updated = queryset.update(is_read=True)
        self.message_user(request, f'{updated} повідомлень позначено як прочитані.')
    mark_as_read.short_description = 'Позначити як прочитане'
    
    def mark_as_resolved(self, request, queryset):
        """Позначити як вирішене"""
        updated = queryset.update(status='resolved')
        self.message_user(request, f'{updated} повідомлень позначено як вирішені.')
    mark_as_resolved.short_description = 'Позначити як вирішене'
```

### 2. Захист від спаму з Google reCAPTCHA

#### Встановіть пакет:

```bash
pip install django-recaptcha
```

#### У `settings.py`:

```python
INSTALLED_APPS = [
    # ...
    'django_recaptcha',
]

RECAPTCHA_PUBLIC_KEY = config('RECAPTCHA_PUBLIC_KEY', default='')
RECAPTCHA_PRIVATE_KEY = config('RECAPTCHA_PRIVATE_KEY', default='')
```

#### У `forms.py`:

```python
from django_recaptcha.fields import ReCaptchaField
from django_recaptcha.widgets import ReCaptchaV2Checkbox

class ContactForm(forms.ModelForm):
    captcha = ReCaptchaField(widget=ReCaptchaV2Checkbox())
    
    class Meta:
        # ... решта коду
```

### 3. AJAX відправка форми

#### JavaScript код:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('#contact-form');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        const formData = new FormData(form);
        
        fetch(form.action, {
            method: 'POST',
            body: formData,
            headers: {
                'X-Requested-With': 'XMLHttpRequest',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                alert('Повідомлення відправлено!');
                form.reset();
            } else {
                alert('Помилка: ' + data.errors);
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Виникла помилка при відправці форми.');
        });
    });
});
```

### 4. Тести

#### Файл: `apps/contact/tests.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from .models import ContactMessage
from .forms import ContactForm


class ContactFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('contact:contact')
    
    def test_contact_form_valid(self):
        """Тест валідної форми"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough characters.',
        }
        form = ContactForm(data=data)
        self.assertTrue(form.is_valid())
    
    def test_contact_form_invalid_short_message(self):
        """Тест невалідної форми з коротким повідомленням"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'Short',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
    
    def test_contact_view_get(self):
        """Тест GET запиту"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact/contact_form.html')
    
    def test_contact_view_post_valid(self):
        """Тест POST запиту з валідними даними"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough characters.',
        }
        response = self.client.post(self.url, data)
        self.assertEqual(ContactMessage.objects.count(), 1)
        self.assertRedirects(response, reverse('contact:success'))
    
    def test_contact_message_creation(self):
        """Тест створення повідомлення"""
        message = ContactMessage.objects.create(
            name='Test User',
            email='test@example.com',
            subject='Test Subject',
            message='Test message',
        )
        self.assertEqual(str(message), 'Test User - Test Subject')
        self.assertEqual(message.status, 'new')
        self.assertFalse(message.is_read)
```

### 5. Сигнали для автоматичних дій

#### Файл: `apps/contact/signals.py`

```python
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.mail import send_mail
from django.conf import settings
from .models import ContactMessage


@receiver(post_save, sender=ContactMessage)
def notify_admin_new_message(sender, instance, created, **kwargs):
    """Відправка email адміністратору при новому повідомленні"""
    if created:
        send_mail(
            subject=f'Нове повідомлення від {instance.name}',
            message=f'Тема: {instance.subject}\n\nПовідомлення:\n{instance.message}\n\nEmail: {instance.email}',
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[settings.CONTACT_EMAIL],
            fail_silently=True,
        )
```

#### Файл: `apps/contact/apps.py`

```python
from django.apps import AppConfig


class ContactConfig(AppConfig):
    default_auto_field = 'django.db.models.BigAutoField'
    name = 'apps.contact'
    verbose_name = 'Контактні форми'
    
    def ready(self):
        import apps.contact.signals
```

---

## Запуск та тестування

### 1. Виконайте міграції:

```bash
python manage.py makemigrations
python manage.py migrate
```

### 2. Створіть суперкористувача (якщо ще не створено):

```bash
python manage.py createsuperuser
```

### 3. Запустіть сервер:

```bash
python manage.py runserver
```

### 4. Перейдіть за адресами:

- Контактна форма: `http://127.0.0.1:8000/contact/`
- Адмін-панель: `http://127.0.0.1:8000/admin/`
- Список повідомлень: `http://127.0.0.1:8000/contact/messages/`

---

## Висновок

Тепер у вас є повнофункціональна контактна форма з:
- ✅ Валідацією даних
- ✅ Збереженням у базі даних
- ✅ Відправкою email
- ✅ Адмін-панеллю
- ✅ Захистом від CSRF
- ✅ Красивим інтерфейсом
- ✅ Тестами

**Додаткові покращення:**
- Додайте rate limiting для захисту від спаму
- Інтегруйте Google reCAPTCHA
- Додайте файлові вкладення
- Створіть API для мобільних додатків
- Додайте сповіщення через Telegram/Slack

**Корисні посилання:**
- [Django Forms Documentation](https://docs.djangoproject.com/en/stable/topics/forms/)
- [Django Email Documentation](https://docs.djangoproject.com/en/stable/topics/email/)
- [Django Messages Framework](https://docs.djangoproject.com/en/stable/ref/contrib/messages/)
