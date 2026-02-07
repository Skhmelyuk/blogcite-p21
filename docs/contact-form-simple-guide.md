# Гайд по створенню простої контактної форми без бази даних

## Зміст
1. [Вступ](#вступ)
2. [Створення додатку](#створення-додатку)
3. [Створення форми](#створення-форми)
4. [Створення представлення (View)](#створення-представлення-view)
5. [Налаштування URL](#налаштування-url)
6. [Створення шаблону](#створення-шаблону)
7. [Налаштування email](#налаштування-email)
8. [Тестування](#тестування)
9. [Додаткові можливості](#додаткові-можливості)

---

## Вступ

Цей гайд показує, як створити просту контактну форму, яка **не зберігає дані в базі даних**, а лише відправляє email-повідомлення. Це підходить для невеликих сайтів, де не потрібна історія повідомлень.

**Переваги цього підходу:**
- ✅ Простота реалізації
- ✅ Не потрібні міграції бази даних
- ✅ Менше коду для підтримки
- ✅ Швидке впровадження

**Що ми реалізуємо:**
- Форма з полями: ім'я, email, тема, повідомлення
- Валідація даних
- Відправка email-повідомлень адміністратору
- Захист від CSRF
- Красивий інтерфейс

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

## Створення форми

### Файл: `apps/contact/forms.py`

Створіть файл `forms.py` у додатку `contact`:

```python
from django import forms
from django.core.validators import EmailValidator


class ContactForm(forms.Form):
    """Проста контактна форма без моделі"""
    
    name = forms.CharField(
        max_length=100,
        label='Ім\'я',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Введіть ваше ім\'я',
            'required': True,
        }),
        error_messages={
            'required': 'Будь ласка, введіть ваше ім\'я.',
            'max_length': 'Ім\'я не може бути довшим за 100 символів.',
        }
    )
    
    email = forms.EmailField(
        label='Email',
        validators=[EmailValidator(message='Введіть коректну email адресу.')],
        widget=forms.EmailInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'your.email@example.com',
            'required': True,
        }),
        error_messages={
            'required': 'Будь ласка, введіть вашу email адресу.',
            'invalid': 'Введіть коректну email адресу.',
        }
    )
    
    subject = forms.CharField(
        max_length=200,
        label='Тема',
        widget=forms.TextInput(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent',
            'placeholder': 'Тема повідомлення',
            'required': True,
        }),
        error_messages={
            'required': 'Будь ласка, введіть тему повідомлення.',
            'max_length': 'Тема не може бути довшою за 200 символів.',
        }
    )
    
    message = forms.CharField(
        label='Повідомлення',
        widget=forms.Textarea(attrs={
            'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent resize-none',
            'placeholder': 'Ваше повідомлення...',
            'rows': 6,
            'required': True,
        }),
        error_messages={
            'required': 'Будь ласка, введіть ваше повідомлення.',
        }
    )
    
    def clean_name(self):
        """Валідація поля імені"""
        name = self.cleaned_data.get('name')
        if len(name) < 2:
            raise forms.ValidationError(
                'Ім\'я повинно містити щонайменше 2 символи.'
            )
        # Перевірка на спам (тільки цифри)
        if name.isdigit():
            raise forms.ValidationError(
                'Ім\'я не може складатися лише з цифр.'
            )
        return name.strip()
    
    def clean_message(self):
        """Валідація поля повідомлення"""
        message = self.cleaned_data.get('message')
        if len(message) < 10:
            raise forms.ValidationError(
                'Повідомлення повинно містити щонайменше 10 символів.'
            )
        # Перевірка на спам (багато посилань)
        if message.lower().count('http') > 3:
            raise forms.ValidationError(
                'Повідомлення містить занадто багато посилань.'
            )
        return message.strip()
    
    def clean_subject(self):
        """Валідація поля теми"""
        subject = self.cleaned_data.get('subject')
        return subject.strip()
```

---

## Створення представлення (View)

### Файл: `apps/contact/views.py`

```python
from django.shortcuts import render, redirect
from django.contrib import messages
from django.core.mail import send_mail, BadHeaderError
from django.conf import settings
from django.views.generic import FormView
from django.urls import reverse_lazy
from .forms import ContactForm


def contact_view(request):
    """Function-based view для контактної форми"""
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Отримуємо дані з форми
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Формуємо email повідомлення
            email_subject = f"Контактна форма: {subject}"
            email_message = f"""
Нове повідомлення з контактної форми

Від: {name}
Email: {email}
Тема: {subject}

Повідомлення:
{message}

---
Це повідомлення надіслано з контактної форми сайту.
            """
            
            # Відправляємо email
            try:
                send_mail(
                    subject=email_subject,
                    message=email_message,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    recipient_list=[settings.CONTACT_EMAIL],
                    fail_silently=False,
                )
                messages.success(
                    request,
                    'Дякуємо за ваше повідомлення! Ми зв\'яжемося з вами найближчим часом.'
                )
                return redirect('contact:success')
            
            except BadHeaderError:
                messages.error(
                    request,
                    'Виявлено некоректний заголовок email.'
                )
            except Exception as e:
                messages.error(
                    request,
                    f'Виникла помилка при відправці повідомлення. Спробуйте пізніше.'
                )
                # Для розробки можна вивести помилку
                if settings.DEBUG:
                    print(f"Email error: {e}")
        else:
            messages.error(
                request,
                'Будь ласка, виправте помилки у формі.'
            )
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact_form.html', {'form': form})


class ContactFormView(FormView):
    """Class-based view для контактної форми"""
    template_name = 'contact/contact_form.html'
    form_class = ContactForm
    success_url = reverse_lazy('contact:success')
    
    def form_valid(self, form):
        """Обробка валідної форми"""
        # Отримуємо дані з форми
        name = form.cleaned_data['name']
        email = form.cleaned_data['email']
        subject = form.cleaned_data['subject']
        message = form.cleaned_data['message']
        
        # Формуємо email повідомлення
        email_subject = f"Контактна форма: {subject}"
        email_message = f"""
Нове повідомлення з контактної форми

Від: {name}
Email: {email}
Тема: {subject}

Повідомлення:
{message}

---
Це повідомлення надіслано з контактної форми сайту.
        """
        
        # Відправляємо email
        try:
            send_mail(
                subject=email_subject,
                message=email_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[settings.CONTACT_EMAIL],
                fail_silently=False,
            )
            messages.success(
                self.request,
                'Дякуємо за ваше повідомлення! Ми зв\'яжемося з вами найближчим часом.'
            )
        except BadHeaderError:
            messages.error(
                self.request,
                'Виявлено некоректний заголовок email.'
            )
            return self.form_invalid(form)
        except Exception as e:
            messages.error(
                self.request,
                'Виникла помилка при відправці повідомлення. Спробуйте пізніше.'
            )
            if settings.DEBUG:
                print(f"Email error: {e}")
            return self.form_invalid(form)
        
        return super().form_valid(form)
    
    def form_invalid(self, form):
        """Обробка невалідної форми"""
        messages.error(
            self.request,
            'Будь ласка, виправте помилки у формі.'
        )
        return super().form_invalid(form)


def contact_success_view(request):
    """Сторінка успішної відправки"""
    return render(request, 'contact/success.html')
```

---

## Налаштування URL

### Файл: `apps/contact/urls.py`

Створіть файл `urls.py` у додатку `contact`:

```python
from django.urls import path
from . import views

app_name = 'contact'

urlpatterns = [
    # Function-based view
    path('', views.contact_view, name='contact'),
    
    # Або використовуйте class-based view (закоментуйте рядок вище)
    # path('', views.ContactFormView.as_view(), name='contact'),
    
    path('success/', views.contact_success_view, name='success'),
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
    path('', include('apps.main.urls', namespace='main')),
    path('cart/', include('apps.cart.urls', namespace='cart')),
    path('accounts/', include('apps.accounts.urls', namespace='accounts')),
    path('contact/', include('apps.contact.urls', namespace='contact')),  # Додайте цей рядок
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
```

---

## Створення шаблону

### Структура папок

Створіть структуру папок для шаблонів:

```
apps/contact/
├── templates/
│   └── contact/
│       ├── contact_form.html
│       └── success.html
```

### Файл: `apps/contact/templates/contact/contact_form.html`

```html
{% extends 'base.html' %}
{% load static %}

{% block title %}Зв'язатися з нами{% endblock %}

{% block content %}
<div class="max-w-5xl mx-auto px-4 py-12">
    <div class="bg-white rounded-xl shadow-2xl overflow-hidden">
        <div class="bg-gradient-to-r from-blue-600 to-blue-700 text-white px-8 py-6">
            <h2 class="text-3xl font-bold text-center">
                <i class="fas fa-envelope mr-3"></i>
                Зв'язатися з нами
            </h2>
        </div>
        <div class="p-8">
            {% if messages %}
                {% for message in messages %}
                    <div class="mb-4 p-4 rounded-lg {% if message.tags == 'success' %}bg-green-100 border border-green-400 text-green-800{% elif message.tags == 'error' %}bg-red-100 border border-red-400 text-red-800{% elif message.tags == 'warning' %}bg-yellow-100 border border-yellow-400 text-yellow-800{% else %}bg-blue-100 border border-blue-400 text-blue-800{% endif %}">
                        {{ message }}
                    </div>
                {% endfor %}
            {% endif %}

            <p class="text-gray-600 mb-6 flex items-center">
                <i class="fas fa-info-circle mr-2 text-blue-500"></i>
                Маєте питання або пропозиції? Заповніть форму нижче, і ми зв'яжемося з вами найближчим часом.
            </p>

            <form method="post" novalidate>
                {% csrf_token %}
                
                <div class="mb-5">
                    <label for="{{ form.name.id_for_label }}" class="block text-sm font-semibold text-gray-700 mb-2">
                        <i class="fas fa-user mr-1 text-blue-500"></i>
                        {{ form.name.label }} <span class="text-red-500">*</span>
                    </label>
                    {{ form.name }}
                    {% if form.name.errors %}
                        {% for error in form.name.errors %}
                            <p class="mt-2 text-sm text-red-600 flex items-center">
                                <i class="fas fa-exclamation-circle mr-1"></i>{{ error }}
                            </p>
                        {% endfor %}
                    {% endif %}
                </div>

                <div class="mb-5">
                    <label for="{{ form.email.id_for_label }}" class="block text-sm font-semibold text-gray-700 mb-2">
                        <i class="fas fa-envelope mr-1 text-blue-500"></i>
                        {{ form.email.label }} <span class="text-red-500">*</span>
                    </label>
                    {{ form.email }}
                    {% if form.email.errors %}
                        {% for error in form.email.errors %}
                            <p class="mt-2 text-sm text-red-600 flex items-center">
                                <i class="fas fa-exclamation-circle mr-1"></i>{{ error }}
                            </p>
                        {% endfor %}
                    {% endif %}
                </div>

                <div class="mb-5">
                    <label for="{{ form.subject.id_for_label }}" class="block text-sm font-semibold text-gray-700 mb-2">
                        <i class="fas fa-tag mr-1 text-blue-500"></i>
                        {{ form.subject.label }} <span class="text-red-500">*</span>
                    </label>
                    {{ form.subject }}
                    {% if form.subject.errors %}
                        {% for error in form.subject.errors %}
                            <p class="mt-2 text-sm text-red-600 flex items-center">
                                <i class="fas fa-exclamation-circle mr-1"></i>{{ error }}
                            </p>
                        {% endfor %}
                    {% endif %}
                </div>

                <div class="mb-6">
                    <label for="{{ form.message.id_for_label }}" class="block text-sm font-semibold text-gray-700 mb-2">
                        <i class="fas fa-comment-dots mr-1 text-blue-500"></i>
                        {{ form.message.label }} <span class="text-red-500">*</span>
                    </label>
                    {{ form.message }}
                    {% if form.message.errors %}
                        {% for error in form.message.errors %}
                            <p class="mt-2 text-sm text-red-600 flex items-center">
                                <i class="fas fa-exclamation-circle mr-1"></i>{{ error }}
                            </p>
                        {% endfor %}
                    {% endif %}
                    <p class="mt-2 text-xs text-gray-500">
                        Мінімум 10 символів
                    </p>
                </div>

                <button type="submit" class="w-full bg-gradient-to-r from-blue-600 to-blue-700 hover:from-blue-700 hover:to-blue-800 text-white font-bold py-4 px-6 rounded-lg transition duration-200 transform hover:scale-[1.02] shadow-lg">
                    <i class="fas fa-paper-plane mr-2"></i>
                    Відправити повідомлення
                </button>
            </form>
        </div>
    </div>

    <!-- Контактна інформація -->
    <div class="grid grid-cols-1 md:grid-cols-3 gap-6 mt-8">
        <div class="bg-white rounded-lg shadow-lg p-6 text-center transform transition duration-200 hover:scale-105">
            <div class="mb-4">
                <i class="fas fa-envelope text-5xl text-blue-600"></i>
            </div>
            <h5 class="text-lg font-bold text-gray-800 mb-2">Email</h5>
            <p class="text-gray-600">info@example.com</p>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6 text-center transform transition duration-200 hover:scale-105">
            <div class="mb-4">
                <i class="fas fa-phone text-5xl text-blue-600"></i>
            </div>
            <h5 class="text-lg font-bold text-gray-800 mb-2">Телефон</h5>
            <p class="text-gray-600">+380 XX XXX XX XX</p>
        </div>
        <div class="bg-white rounded-lg shadow-lg p-6 text-center transform transition duration-200 hover:scale-105">
            <div class="mb-4">
                <i class="fas fa-map-marker-alt text-5xl text-blue-600"></i>
            </div>
            <h5 class="text-lg font-bold text-gray-800 mb-2">Адреса</h5>
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
    <div class="bg-white rounded-xl shadow-2xl text-center p-12">
        <div class="mb-6 animate-bounce">
            <i class="fas fa-check-circle text-8xl text-green-500"></i>
        </div>
        <h2 class="text-4xl font-bold text-gray-800 mb-4">Дякуємо!</h2>
        <p class="text-lg text-gray-600 mb-8 leading-relaxed">
            Ваше повідомлення успішно відправлено. 
            Ми зв'яжемося з вами найближчим часом.
        </p>
        <div class="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="{% url 'main:post_list' %}" class="inline-flex items-center justify-center bg-blue-600 hover:bg-blue-700 text-white font-semibold py-3 px-8 rounded-lg transition duration-200 transform hover:scale-105">
                <i class="fas fa-home mr-2"></i>
                На головну
            </a>
            <a href="{% url 'contact:contact' %}" class="inline-flex items-center justify-center bg-white hover:bg-gray-50 text-gray-700 font-semibold py-3 px-8 rounded-lg border-2 border-gray-300 transition duration-200 transform hover:scale-105">
                <i class="fas fa-envelope mr-2"></i>
                Надіслати ще
            </a>
        </div>
    </div>
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
# Email налаштування
EMAIL_HOST=smtp.gmail.com
EMAIL_PORT=587
EMAIL_USE_TLS=True
EMAIL_HOST_USER=your-email@gmail.com
EMAIL_HOST_PASSWORD=your-app-password
DEFAULT_FROM_EMAIL=noreply@example.com
CONTACT_EMAIL=admin@example.com
```

### Опис email змінних

#### **EMAIL_HOST**
**Призначення:** Адреса SMTP сервера, через який відправляються email листи.

**Приклади:**
- Gmail: `smtp.gmail.com`
- Outlook/Hotmail: `smtp-mail.outlook.com`
- Yahoo: `smtp.mail.yahoo.com`
- Власний сервер: адреса вашого SMTP сервера

#### **EMAIL_PORT**
**Призначення:** Порт SMTP сервера для з'єднання.

**Варіанти:**
- `587` - стандартний порт для TLS (рекомендовано)
- `465` - порт для SSL
- `25` - незахищений порт (не рекомендується)

#### **EMAIL_USE_TLS**
**Призначення:** Увімкнення шифрування TLS (Transport Layer Security) для безпечної передачі даних.

**Значення:**
- `True` - використовувати TLS шифрування (рекомендовано для порту 587)
- `False` - без шифрування (небезпечно)

#### **EMAIL_HOST_USER**
**Призначення:** Email адреса для автентифікації на SMTP сервері (логін).

**Особливості:**
- Це ваша Gmail адреса
- Використовується для входу на SMTP сервер
- З цієї адреси технічно відправляються листи

**Приклад:** `your-email@gmail.com`

#### **EMAIL_HOST_PASSWORD**
**Призначення:** Пароль для автентифікації на SMTP сервері.

**Важливо:**
- **НЕ** ваш звичайний пароль від Gmail!
- Це **пароль додатку** (App Password) - спеціальний 16-символьний код
- Генерується в налаштуваннях безпеки Google
- Використовується замість основного пароля для підвищення безпеки
- Формат: `xxxx xxxx xxxx xxxx` (можна з пробілами або без)

#### **DEFAULT_FROM_EMAIL**
**Призначення:** Email адреса, яка відображається в полі "Від кого" (From) у листах.

**Особливості:**
- Це адреса, яку побачить одержувач як відправника
- Зазвичай збігається з `EMAIL_HOST_USER`
- Може бути іншою, але Gmail може заблокувати, якщо адреси не співпадають

**Приклад листа:**
```
Від: noreply@example.com
Кому: admin@example.com
Тема: Контактна форма: Питання про продукт
```

#### **CONTACT_EMAIL**
**Призначення:** Email адреса, **на яку приходять** повідомлення з контактної форми.

**Особливості:**
- Це адреса одержувача (адміністратора)
- Сюди надсилаються всі повідомлення з форми
- Може бути будь-якою адресою (не обов'язково Gmail)
- Можна вказати кілька адрес через кому

**Використання в коді:**
```python
send_mail(
    subject="Нове повідомлення",
    message="...",
    from_email=DEFAULT_FROM_EMAIL,  # Від кого
    recipient_list=[CONTACT_EMAIL],  # Кому
)
```

### Схема роботи email

```
Користувач заповнює форму
         ↓
Django відправляє email через SMTP
         ↓
SMTP сервер (smtp.gmail.com:587)
    ├─ Автентифікація: EMAIL_HOST_USER + EMAIL_HOST_PASSWORD
    ├─ Шифрування: EMAIL_USE_TLS
    └─ Відправка
         ↓
Email доставляється
    ├─ Від: DEFAULT_FROM_EMAIL
    └─ Кому: CONTACT_EMAIL
```

### Для розробки (виведення email у консоль):

```python
# У settings.py для розробки
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

### Налаштування Gmail

Для використання Gmail:

1. Увійдіть у свій Google акаунт
2. Перейдіть до налаштувань безпеки
3. Увімкніть двофакторну автентифікацію
4. Створіть пароль додатку (App Password)
5. Використовуйте цей пароль у `EMAIL_HOST_PASSWORD`

---

## Тестування

### 1. Запустіть сервер

```bash
python manage.py runserver
```

### 2. Відкрийте форму

Перейдіть за адресою: `http://127.0.0.1:8000/contact/`

### 3. Тестування у консолі

Якщо використовуєте `console.EmailBackend`, email з'явиться у консолі:

```
Content-Type: text/plain; charset="utf-8"
MIME-Version: 1.0
Content-Transfer-Encoding: 7bit
Subject: Контактна форма: Тестова тема
From: noreply@example.com
To: admin@example.com
Date: Fri, 07 Feb 2026 07:00:00 -0000
Message-ID: <...>

Нове повідомлення з контактної форми

Від: Тестовий Користувач
Email: test@example.com
Тема: Тестова тема

Повідомлення:
Це тестове повідомлення для перевірки контактної форми.
```

### 4. Тести

#### Файл: `apps/contact/tests.py`

```python
from django.test import TestCase, Client
from django.urls import reverse
from django.core import mail
from .forms import ContactForm


class ContactFormTests(TestCase):
    def setUp(self):
        self.client = Client()
        self.url = reverse('contact:contact')
    
    def test_contact_form_valid_data(self):
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
        self.assertIn('message', form.errors)
    
    def test_contact_form_invalid_short_name(self):
        """Тест невалідної форми з коротким ім'ям"""
        data = {
            'name': 'A',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message.',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_contact_form_invalid_email(self):
        """Тест невалідної email адреси"""
        data = {
            'name': 'Test User',
            'email': 'invalid-email',
            'subject': 'Test Subject',
            'message': 'This is a test message.',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('email', form.errors)
    
    def test_contact_view_get(self):
        """Тест GET запиту"""
        response = self.client.get(self.url)
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact/contact_form.html')
        self.assertIsInstance(response.context['form'], ContactForm)
    
    def test_contact_view_post_valid(self):
        """Тест POST запиту з валідними даними"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test Subject',
            'message': 'This is a test message with enough characters.',
        }
        response = self.client.post(self.url, data)
        
        # Перевірка редіректу
        self.assertRedirects(response, reverse('contact:success'))
        
        # Перевірка відправки email
        self.assertEqual(len(mail.outbox), 1)
        self.assertIn('Test Subject', mail.outbox[0].subject)
        self.assertIn('test@example.com', mail.outbox[0].body)
    
    def test_contact_view_post_invalid(self):
        """Тест POST запиту з невалідними даними"""
        data = {
            'name': 'A',
            'email': 'invalid-email',
            'subject': '',
            'message': 'Short',
        }
        response = self.client.post(self.url, data)
        
        # Форма повинна бути невалідною
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response, 'form', 'name', 
                           'Ім\'я повинно містити щонайменше 2 символи.')
        
        # Email не повинен бути відправлений
        self.assertEqual(len(mail.outbox), 0)
    
    def test_success_page(self):
        """Тест сторінки успіху"""
        response = self.client.get(reverse('contact:success'))
        self.assertEqual(response.status_code, 200)
        self.assertTemplateUsed(response, 'contact/success.html')


class ContactFormSpamProtectionTests(TestCase):
    def test_name_only_digits(self):
        """Тест захисту від спаму - ім'я тільки з цифр"""
        data = {
            'name': '12345',
            'email': 'test@example.com',
            'subject': 'Test',
            'message': 'This is a test message.',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('name', form.errors)
    
    def test_message_too_many_links(self):
        """Тест захисту від спаму - багато посилань"""
        data = {
            'name': 'Test User',
            'email': 'test@example.com',
            'subject': 'Test',
            'message': 'http://spam1.com http://spam2.com http://spam3.com http://spam4.com',
        }
        form = ContactForm(data=data)
        self.assertFalse(form.is_valid())
        self.assertIn('message', form.errors)
```

### Запуск тестів

```bash
python manage.py test apps.contact
```

---

## Додаткові можливості

### 1. HTML Email з шаблоном

#### Файл: `apps/contact/templates/contact/email/contact_email.html`

```html
<!DOCTYPE html>
<html>
<head>
    <style>
        body { font-family: Arial, sans-serif; line-height: 1.6; }
        .container { max-width: 600px; margin: 0 auto; padding: 20px; }
        .header { background-color: #007bff; color: white; padding: 20px; text-align: center; }
        .content { background-color: #f8f9fa; padding: 20px; margin: 20px 0; }
        .footer { text-align: center; color: #6c757d; font-size: 12px; }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h2>Нове повідомлення з контактної форми</h2>
        </div>
        <div class="content">
            <p><strong>Від:</strong> {{ name }}</p>
            <p><strong>Email:</strong> {{ email }}</p>
            <p><strong>Тема:</strong> {{ subject }}</p>
            <hr>
            <p><strong>Повідомлення:</strong></p>
            <p>{{ message|linebreaks }}</p>
        </div>
        <div class="footer">
            <p>Це повідомлення надіслано з контактної форми вашого сайту.</p>
        </div>
    </div>
</body>
</html>
```

#### Оновлений view з HTML email:

```python
from django.core.mail import send_mail, EmailMultiAlternatives
from django.template.loader import render_to_string

def contact_view(request):
    if request.method == 'POST':
        form = ContactForm(request.POST)
        if form.is_valid():
            # Отримуємо дані
            name = form.cleaned_data['name']
            email = form.cleaned_data['email']
            subject = form.cleaned_data['subject']
            message = form.cleaned_data['message']
            
            # Створюємо HTML email
            html_content = render_to_string('contact/email/contact_email.html', {
                'name': name,
                'email': email,
                'subject': subject,
                'message': message,
            })
            
            text_content = f"""
Нове повідомлення з контактної форми

Від: {name}
Email: {email}
Тема: {subject}

Повідомлення:
{message}
            """
            
            # Відправляємо email
            try:
                email_message = EmailMultiAlternatives(
                    subject=f"Контактна форма: {subject}",
                    body=text_content,
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[settings.CONTACT_EMAIL],
                    reply_to=[email],
                )
                email_message.attach_alternative(html_content, "text/html")
                email_message.send()
                
                messages.success(request, 'Дякуємо за ваше повідомлення!')
                return redirect('contact:success')
            except Exception as e:
                messages.error(request, 'Помилка при відправці повідомлення.')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact_form.html', {'form': form})
```

### 2. AJAX відправка форми

#### JavaScript:

```javascript
document.addEventListener('DOMContentLoaded', function() {
    const form = document.querySelector('form');
    const submitBtn = form.querySelector('button[type="submit"]');
    
    form.addEventListener('submit', function(e) {
        e.preventDefault();
        
        // Блокуємо кнопку
        submitBtn.disabled = true;
        submitBtn.innerHTML = '<i class="fas fa-spinner fa-spin me-2"></i>Відправка...';
        
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
                // Показуємо повідомлення успіху
                alert('Повідомлення відправлено!');
                form.reset();
            } else {
                // Показуємо помилки
                alert('Помилка: ' + JSON.stringify(data.errors));
            }
        })
        .catch(error => {
            console.error('Error:', error);
            alert('Виникла помилка при відправці форми.');
        })
        .finally(() => {
            // Розблоковуємо кнопку
            submitBtn.disabled = false;
            submitBtn.innerHTML = '<i class="fas fa-paper-plane me-2"></i>Відправити повідомлення';
        });
    });
});
```

### 3. Rate Limiting (обмеження частоти запитів)

```python
from django.core.cache import cache
from django.http import HttpResponseForbidden

def contact_view(request):
    if request.method == 'POST':
        # Перевірка rate limit
        ip = request.META.get('REMOTE_ADDR')
        cache_key = f'contact_form_{ip}'
        
        if cache.get(cache_key):
            messages.error(
                request,
                'Ви вже відправили повідомлення. Спробуйте через 5 хвилин.'
            )
            return redirect('contact:contact')
        
        form = ContactForm(request.POST)
        if form.is_valid():
            # ... відправка email ...
            
            # Встановлюємо обмеження на 5 хвилин
            cache.set(cache_key, True, 300)
            
            return redirect('contact:success')
    else:
        form = ContactForm()
    
    return render(request, 'contact/contact_form.html', {'form': form})
```

### 4. Копія листа відправнику

```python
# Відправка копії листа користувачу
try:
    # Email адміністратору
    send_mail(...)
    
    # Копія користувачу
    send_mail(
        subject='Дякуємо за ваше повідомлення',
        message=f'Шановний(а) {name},\n\nДякуємо за ваше повідомлення. Ми отримали його і зв\'яжемося з вами найближчим часом.\n\nВаше повідомлення:\n{message}',
        from_email=settings.DEFAULT_FROM_EMAIL,
        recipient_list=[email],
        fail_silently=True,
    )
except Exception as e:
    pass
```

---

## Висновок

Тепер у вас є проста контактна форма без бази даних з:

- ✅ Валідацією даних
- ✅ Відправкою email
- ✅ Захистом від CSRF
- ✅ Красивим інтерфейсом
- ✅ Тестами
- ✅ Захистом від спаму

**Переваги:**
- Проста у впровадженні
- Не потребує міграцій
- Мінімум коду

**Недоліки:**
- Немає історії повідомлень
- Неможливо переглянути старі повідомлення
- Залежність від email сервісу

**Коли використовувати:**
- Невеликі сайти
- Прості контактні форми
- Коли не потрібна історія

**Коли НЕ використовувати:**
- Потрібна історія повідомлень
- Потрібна статистика
- Потрібна адмін-панель для управління

**Наступні кроки:**
- Додайте Google reCAPTCHA
- Налаштуйте реальний SMTP сервер
- Додайте файлові вкладення
- Створіть кілька варіантів форм
