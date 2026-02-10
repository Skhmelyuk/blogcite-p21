# Гайд: Створення кастомних тегів і фільтрів у Django

## Зміст
1. [Вступ](#вступ)
2. [Структура проекту](#структура-проекту)
3. [Створення фільтрів](#створення-фільтрів)
4. [Створення тегів](#створення-тегів)
5. [Використання в шаблонах](#використання-в-шаблонах)
6. [Додаткові приклади](#додаткові-приклади)

---

## Вступ

**Кастомні теги та фільтри** дозволяють розширити функціональність шаблонів Django, додаючи власну логіку обробки даних безпосередньо в HTML-шаблонах.

### Різниця між тегами і фільтрами:

- **Фільтри** (`@register.filter`) - модифікують значення змінної через pipe `|`
  ```django
  {{ post.content|reading_time }}
  ```

- **Теги** (`@register.simple_tag`) - виконують складнішу логіку, можуть приймати кілька аргументів
  ```django
  {% posts_count_in_category category %}
  ```

---

## Структура проекту

Для роботи з кастомними тегами потрібно створити наступну структуру:

```
blogcite-p21/
└── apps/
    └── main/
        ├── templatetags/          # Новий каталог
        │   ├── __init__.py        # Обов'язковий порожній файл
        │   ├── blog_filters.py    # Файл з фільтрами
        │   └── blog_tags.py       # Файл з тегами
        ├── models.py
        ├── views.py
        └── ...
```

### Крок 1: Створення директорії `templatetags`

```bash
mkdir -p apps/main/templatetags
touch apps/main/templatetags/__init__.py
```

---

## Створення фільтрів

### Файл: `apps/main/templatetags/blog_filters.py`

```python
from django import template
import re
from django.utils.html import strip_tags

register = template.Library()

# ============================================
# ФІЛЬТР 1: Час читання статті
# ============================================
@register.filter
def reading_time(text):
    """
    Обчислює приблизний час читання статті.
    Середня швидкість читання: 200 слів/хвилину
    
    Використання: {{ post.content|reading_time }}
    """
    # Видаляємо HTML теги
    text = re.sub(r'<[^>]+>', '', str(text))
    
    # Рахуємо слова
    words = len(text.split())
    
    # Обчислюємо час
    minutes = words / 200
    
    if minutes < 1:
        return "менше 1 хвилини"
    elif minutes < 2:
        return "1 хвилина"
    else:
        return f"{int(minutes)} хвилин"


# ============================================
# ФІЛЬТР 2: Компактне відображення чисел
# ============================================
@register.filter
def compact_views(value):
    """
    Скорочує великі числа переглядів:
    1000 → 1K
    1500 → 1.5K
    1000000 → 1M
    
    Використання: {{ post.views|compact_views }}
    """
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value / 1000000:.1f}M"
        elif value >= 1000:
            return f"{value / 1000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return value


# ============================================
# ФІЛЬТР 3: Відносний час ("назад")
# ============================================
@register.filter
def time_ago(date):
    """
    Відображає час у форматі 'назад':
    - щойно
    - 5 хв тому
    - 2 год тому
    - 3 дн тому
    
    Використання: {{ post.created_at|time_ago }}
    """
    from django.utils import timezone
    
    now = timezone.now()
    diff = now - date
    seconds = diff.total_seconds()
    
    if seconds < 60:
        return "щойно"
    elif seconds < 3600:
        minutes = int(seconds / 60)
        return f"{minutes} хв тому"
    elif seconds < 86400:
        hours = int(seconds / 3600)
        return f"{hours} год тому"
    elif seconds < 604800:
        days = int(seconds / 86400)
        return f"{days} дн тому"
    else:
        return date.strftime("%d.%m.%Y")


# ============================================
# ФІЛЬТР 4: Скорочення тексту з трьома крапками
# ============================================
@register.filter
def truncate_words_custom(text, length=50):
    """
    Обрізає текст до вказаної кількості слів і додає "..."
    
    Використання: {{ post.content|truncate_words_custom:30 }}
    """
    text = strip_tags(str(text))
    words = text.split()
    
    if len(words) <= length:
        return text
    
    return ' '.join(words[:length]) + '...'


# ============================================
# ФІЛЬТР 5: Підрахунок коментарів (якщо є модель Comment)
# ============================================
@register.filter
def comments_count(post):
    """
    Повертає кількість коментарів до поста
    
    Використання: {{ post|comments_count }}
    """
    # Якщо у вас є модель Comment з ForeignKey до Post
    # return post.comment_set.count()
    
    # Поки що повертаємо 0 (приклад)
    return 0


# ============================================
# ФІЛЬТР 6: Форматування лайків
# ============================================
@register.filter
def format_likes(value):
    """
    Форматує кількість лайків з іконкою
    
    Використання: {{ post.likes|format_likes }}
    """
    try:
        value = int(value)
        if value == 0:
            return "❤️ Без лайків"
        elif value == 1:
            return "❤️ 1 лайк"
        elif value < 5:
            return f"❤️ {value} лайки"
        else:
            return f"❤️ {value} лайків"
    except (ValueError, TypeError):
        return value


# ============================================
# ФІЛЬТР 7: Перевірка чи пост новий (менше 7 днів)
# ============================================
@register.filter
def is_new(date):
    """
    Перевіряє чи пост новий (створений менше 7 днів тому)
    
    Використання: {% if post.created_at|is_new %}NEW!{% endif %}
    """
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    diff = now - date
    
    return diff < timedelta(days=7)


# ============================================
# ФІЛЬТР 8: Виділення першого речення
# ============================================
@register.filter
def first_sentence(text):
    """
    Повертає перше речення з тексту
    
    Використання: {{ post.content|first_sentence }}
    """
    text = strip_tags(str(text))
    
    # Шукаємо перший знак кінця речення
    for delimiter in ['. ', '! ', '? ']:
        if delimiter in text:
            return text.split(delimiter)[0] + delimiter.strip()
    
    # Якщо не знайдено, повертаємо перші 100 символів
    return text[:100] + '...' if len(text) > 100 else text
```

---

## Створення тегів

### Файл: `apps/main/templatetags/blog_tags.py`

```python
from django import template
from apps.main.models import Post, Category
from django.db.models import Count

register = template.Library()


# ============================================
# ТЕГ 1: Кількість постів у категорії
# ============================================
@register.simple_tag
def posts_count_in_category(category):
    """
    Повертає кількість постів у категорії
    
    Використання: {% posts_count_in_category category %}
    """
    return Post.objects.filter(category=category).count()


# ============================================
# ТЕГ 2: Останні N постів
# ============================================
@register.simple_tag
def get_recent_posts(count=5):
    """
    Повертає останні N постів
    
    Використання: {% get_recent_posts 5 as recent_posts %}
    """
    return Post.objects.all().order_by('-created_at')[:count]


# ============================================
# ТЕГ 3: Найпопулярніші пости
# ============================================
@register.simple_tag
def get_popular_posts(count=5):
    """
    Повертає найпопулярніші пости за кількістю переглядів
    
    Використання: {% get_popular_posts 5 as popular_posts %}
    """
    return Post.objects.all().order_by('-views')[:count]


# ============================================
# ТЕГ 4: Категорії з кількістю постів
# ============================================
@register.simple_tag
def get_categories_with_count():
    """
    Повертає всі категорії з кількістю постів у кожній
    
    Використання: {% get_categories_with_count as categories %}
    """
    return Category.objects.annotate(
        posts_count=Count('post')
    ).filter(posts_count__gt=0)


# ============================================
# ТЕГ 5: Загальна кількість постів
# ============================================
@register.simple_tag
def total_posts_count():
    """
    Повертає загальну кількість постів
    
    Використання: {% total_posts_count %}
    """
    return Post.objects.count()


# ============================================
# ТЕГ 6: Загальна кількість переглядів
# ============================================
@register.simple_tag
def total_views_count():
    """
    Повертає загальну кількість переглядів всіх постів
    
    Використання: {% total_views_count %}
    """
    from django.db.models import Sum
    result = Post.objects.aggregate(total=Sum('views'))
    return result['total'] or 0


# ============================================
# ТЕГ 7: Пости того ж автора
# ============================================
@register.simple_tag
def get_author_posts(author, exclude_post_id=None, count=5):
    """
    Повертає інші пости того ж автора
    
    Використання: {% get_author_posts post.author post.id 3 as author_posts %}
    """
    posts = Post.objects.filter(author=author)
    
    if exclude_post_id:
        posts = posts.exclude(id=exclude_post_id)
    
    return posts.order_by('-created_at')[:count]


# ============================================
# ТЕГ 8: Схожі пости (за категорією)
# ============================================
@register.simple_tag
def get_related_posts(post, count=4):
    """
    Повертає схожі пости з тієї ж категорії
    
    Використання: {% get_related_posts post 4 as related_posts %}
    """
    if not post.category:
        return Post.objects.none()
    
    return Post.objects.filter(
        category=post.category
    ).exclude(id=post.id).order_by('-created_at')[:count]


# ============================================
# ТЕГ 9: Перевірка чи є пости в категорії
# ============================================
@register.simple_tag
def has_posts_in_category(category):
    """
    Перевіряє чи є пости в категорії
    
    Використання: {% has_posts_in_category category as has_posts %}
    """
    return Post.objects.filter(category=category).exists()


# ============================================
# ТЕГ 10: Рандомний пост
# ============================================
@register.simple_tag
def get_random_post():
    """
    Повертає випадковий пост
    
    Використання: {% get_random_post as random_post %}
    """
    return Post.objects.order_by('?').first()
```

---

## Використання в шаблонах

### 1. Завантаження тегів і фільтрів

На початку шаблону потрібно завантажити модулі:

```django
{% load blog_filters %}
{% load blog_tags %}
```

### 2. Приклад використання фільтрів

**Файл: `apps/main/templates/main/post_detail.html`**

```django
{% extends 'main/base.html' %}
{% load blog_filters %}

{% block content %}
<article class="post-detail">
    <h1>{{ post.title }}</h1>
    
    <div class="post-meta">
        <!-- Час читання -->
        <span>📖 Час читання: {{ post.content|reading_time }}</span>
        
        <!-- Компактні перегляди -->
        <span>👁️ {{ post.views|compact_views }} переглядів</span>
        
        <!-- Відносний час -->
        <span>🕒 Опубліковано: {{ post.created_at|time_ago }}</span>
        
        <!-- Лайки -->
        <span>{{ post.likes|format_likes }}</span>
        
        <!-- Значок "NEW" для нових постів -->
        {% if post.created_at|is_new %}
            <span class="badge badge-new">🆕 NEW!</span>
        {% endif %}
    </div>
    
    <!-- Перше речення як анонс -->
    <p class="lead">{{ post.content|first_sentence }}</p>
    
    <!-- Повний контент -->
    <div class="post-content">
        {{ post.content|safe }}
    </div>
</article>
{% endblock %}
```

### 3. Приклад використання тегів

**Файл: `apps/main/templates/main/base.html`**

```django
{% load static %}
{% load blog_tags %}

<!DOCTYPE html>
<html lang="uk">
<head>
    <meta charset="UTF-8">
    <title>{% block title %}Мій Блог{% endblock %}</title>
</head>
<body>
    <header>
        <nav>
            <!-- Загальна статистика -->
            <div class="stats">
                <span>📝 Всього постів: {% total_posts_count %}</span>
                <span>👁️ Всього переглядів: {% total_views_count %}</span>
            </div>
        </nav>
    </header>

    <aside class="sidebar">
        <!-- Категорії з кількістю постів -->
        <h3>Категорії</h3>
        <ul>
            {% get_categories_with_count as categories %}
            {% for category in categories %}
                <li>
                    <a href="{{ category.get_absolute_url }}">
                        {{ category.name }}
                        <span class="badge">{% posts_count_in_category category %}</span>
                    </a>
                </li>
            {% endfor %}
        </ul>

        <!-- Популярні пости -->
        <h3>Популярні пости</h3>
        {% get_popular_posts 5 as popular_posts %}
        <ul>
            {% for post in popular_posts %}
                <li>
                    <a href="{{ post.get_absolute_url }}">
                        {{ post.title }}
                        <small>({{ post.views|compact_views }} переглядів)</small>
                    </a>
                </li>
            {% endfor %}
        </ul>

        <!-- Останні пости -->
        <h3>Останні пости</h3>
        {% get_recent_posts 5 as recent_posts %}
        <ul>
            {% for post in recent_posts %}
                <li>
                    <a href="{{ post.get_absolute_url }}">
                        {{ post.title }}
                        {% if post.created_at|is_new %}
                            <span class="badge-new">NEW</span>
                        {% endif %}
                    </a>
                </li>
            {% endfor %}
        </ul>
    </aside>

    <main>
        {% block content %}{% endblock %}
    </main>
</body>
</html>
```

### 4. Схожі пости на сторінці деталей

**Файл: `apps/main/templates/main/post_detail.html`** (продовження)

```django
<!-- Схожі пости -->
<section class="related-posts">
    <h2>Схожі статті</h2>
    {% get_related_posts post 4 as related_posts %}
    
    {% if related_posts %}
        <div class="posts-grid">
            {% for related_post in related_posts %}
                <article class="post-card">
                    <h3>
                        <a href="{{ related_post.get_absolute_url }}">
                            {{ related_post.title }}
                        </a>
                    </h3>
                    <p>{{ related_post.content|truncate_words_custom:20 }}</p>
                    <div class="meta">
                        <span>{{ related_post.created_at|time_ago }}</span>
                        <span>{{ related_post.views|compact_views }} переглядів</span>
                    </div>
                </article>
            {% endfor %}
        </div>
    {% endif %}
</section>

<!-- Інші пости автора -->
<section class="author-posts">
    <h2>Інші статті автора {{ post.author.username }}</h2>
    {% get_author_posts post.author post.id 3 as author_posts %}
    
    {% if author_posts %}
        <ul>
            {% for author_post in author_posts %}
                <li>
                    <a href="{{ author_post.get_absolute_url }}">
                        {{ author_post.title }}
                    </a>
                    <small>({{ author_post.created_at|time_ago }})</small>
                </li>
            {% endfor %}
        </ul>
    {% endif %}
</section>
```

---

## Додаткові приклади

### Приклад 1: Комбінування фільтрів

```django
<!-- Скорочений текст з компактними переглядами -->
<p>{{ post.content|truncate_words_custom:30 }}</p>
<span>{{ post.views|compact_views }} переглядів {{ post.created_at|time_ago }}</span>
```

### Приклад 2: Умовне відображення

```django
{% if post.created_at|is_new %}
    <div class="alert alert-info">
        🎉 Це новий пост! Опублікований {{ post.created_at|time_ago }}
    </div>
{% endif %}
```

### Приклад 3: Список постів з метаданими

```django
{% load blog_filters %}
{% load blog_tags %}

<div class="posts-list">
    {% for post in posts %}
        <article class="post-item">
            <h2>
                <a href="{{ post.get_absolute_url }}">{{ post.title }}</a>
                {% if post.created_at|is_new %}
                    <span class="badge-new">NEW</span>
                {% endif %}
            </h2>
            
            <p class="excerpt">{{ post.content|first_sentence }}</p>
            
            <div class="post-meta">
                <span>👤 {{ post.author.username }}</span>
                <span>📅 {{ post.created_at|time_ago }}</span>
                <span>👁️ {{ post.views|compact_views }}</span>
                <span>{{ post.likes|format_likes }}</span>
                <span>📖 {{ post.content|reading_time }}</span>
            </div>
        </article>
    {% endfor %}
</div>
```

---

## Важливі примітки

### 1. Перезапуск сервера
Після створення нових тегів/фільтрів **обов'язково перезапустіть** Django сервер:
```bash
python manage.py runserver
```

### 2. Помилки імпорту
Якщо виникає помилка `TemplateDoesNotExist` або `Invalid block tag`, перевірте:
- Чи існує файл `__init__.py` в директорії `templatetags/`
- Чи правильно вказано назву модуля в `{% load ... %}`
- Чи додано додаток до `INSTALLED_APPS` в `settings.py`

### 3. Тестування
Протестуйте кожен фільтр/тег окремо в Django shell:
```python
python manage.py shell

from apps.main.templatetags.blog_filters import reading_time
from apps.main.models import Post

post = Post.objects.first()
print(reading_time(post.content))
```

### 4. Продуктивність
Уникайте складних запитів до БД всередині фільтрів. Краще використовуйте теги з `select_related()` або `prefetch_related()`.

---

## Підсумок

Ви створили:
- ✅ **8 корисних фільтрів** для обробки даних
- ✅ **10 потужних тегів** для роботи з постами та категоріями
- ✅ Повний набір інструментів для покращення UX вашого блогу

**Наступні кроки:**
1. Створіть директорію `templatetags` у вашому додатку
2. Скопіюйте код фільтрів і тегів
3. Завантажте їх у шаблонах через `{% load blog_filters %}` та `{% load blog_tags %}`
4. Налаштуйте відображення згідно з вашим дизайном

Успіхів у розробці! 🚀
