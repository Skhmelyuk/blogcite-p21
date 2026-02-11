# Гайд: Додавання коментарів до постів

## Мета

Додати систему коментарів до блогу. Зареєстровані користувачі зможуть залишати коментарі під постами, а також видаляти **тільки свої** коментарі.

## Що вже є в проекті

- Модель `Post` з полем `author = ForeignKey(User)` (`apps/main/models.py`)
- View `post_detail` для відображення поста (`apps/main/views.py`)
- Шаблон `post_details.html` (`apps/main/templates/main/post_details.html`)
- Авторизація: login, register, profile, logout (`apps/accounts/`)
- `LOGIN_URL = 'accounts:login'` (`config/settings.py`)
- Tailwind CSS для стилізації

## Що потрібно додати/змінити

| Файл | Що додати |
|------|-----------|
| `apps/main/models.py` | Модель `Comment` |
| `apps/main/forms.py` | Форма `CommentForm` |
| `apps/main/views.py` | Логіка додавання та видалення коментарів |
| `apps/main/urls.py` | URL маршрути для коментарів |
| `apps/main/admin.py` | Реєстрація моделі `Comment` в адмінці |
| `templates/main/post_details.html` | Блок коментарів під постом |

---

## Крок 1: Створення моделі Comment

**Файл:** `apps/main/models.py`

Додайте модель `Comment` в кінець файлу (після сигналів):

```python
class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='comments', verbose_name="Пост")
    author = models.ForeignKey(User, on_delete=models.CASCADE, verbose_name="Автор")
    body = models.TextField(verbose_name="Текст коментаря")
    created_at = models.DateTimeField(auto_now_add=True, verbose_name="Дата створення")
    updated_at = models.DateTimeField(auto_now=True, verbose_name="Дата оновлення")

    class Meta:
        ordering = ["-created_at"]
        verbose_name = "Коментар"
        verbose_name_plural = "Коментарі"

    def __str__(self):
        return f"Коментар від {self.author.username} до «{self.post.title}»"
```

### Пояснення:

- **post** — зв'язок з постом через `ForeignKey`. `related_name='comments'` дозволяє отримати всі коментарі поста через `post.comments.all()`
- **author** — зв'язок з користувачем, який залишив коментар
- **body** — текст коментаря
- **ordering = ["-created_at"]** — нові коментарі відображаються першими
- **on_delete=models.CASCADE** — при видаленні поста або користувача, коментарі видаляються автоматично

---

## Крок 2: Створення та застосування міграцій

Після додавання моделі виконайте команди:

```bash
python manage.py makemigrations main
python manage.py migrate
```

Ви побачите щось на кшталт:

```
Migrations for 'main':
  apps/main/migrations/0004_comment.py
    - Create model Comment
```

---

## Крок 3: Реєстрація в адмінці

**Файл:** `apps/main/admin.py`

### 3.1 Додайте імпорт моделі Comment

Змініть рядок імпорту:

```python
from .models import Post, Category, Comment
```

### 3.2 Додайте клас CommentAdmin

В кінець файлу додайте:

```python
@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ("id", "author", "post", "short_body", "created_at")
    list_filter = ("created_at", "author")
    search_fields = ("body", "author__username", "post__title")

    def short_body(self, obj):
        return obj.body[:50] + "..." if len(obj.body) > 50 else obj.body
    short_body.short_description = "Текст"
```

### Пояснення:

- **list_display** — колонки, які відображаються в списку коментарів
- **short_body** — обрізає довгий текст коментаря до 50 символів для зручності
- **list_filter** — фільтрація за датою та автором
- **search_fields** — пошук по тексту коментаря, імені автора та заголовку поста

---

## Крок 4: Створення форми CommentForm

**Файл:** `apps/main/forms.py`

Додайте імпорт моделі та форму в кінець файлу:

```python
from .models import Post, Comment


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ['body']
        widgets = {
            'body': forms.Textarea(attrs={
                'class': 'w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-teal-500 focus:border-transparent resize-none',
                'rows': 4,
                'placeholder': 'Напишіть ваш коментар...',
            }),
        }
        labels = {
            'body': 'Коментар',
        }
```

### Пояснення:

- **fields = ['body']** — користувач заповнює тільки текст коментаря. Поля `post` та `author` встановлюються автоматично у view
- **widgets** — Tailwind CSS класи для стилізації (як і в `PostForm`)

---

## Крок 5: Оновлення Views

**Файл:** `apps/main/views.py`

### 5.1 Додайте імпорти

Змініть рядки імпортів:

```python
from .models import Post, Category, Comment
from .forms import PostForm, CommentForm
```

### 5.2 Оновіть view `post_detail`

Замініть існуючу функцію `post_detail` на нову версію з підтримкою коментарів:

```python
def post_detail(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    post.views += 1
    post.save()

    comments = post.comments.all()
    comment_form = CommentForm()

    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect(f'{settings.LOGIN_URL}?next={request.path}')
        
        comment_form = CommentForm(request.POST)
        if comment_form.is_valid():
            comment = comment_form.save(commit=False)
            comment.post = post
            comment.author = request.user
            comment.save()
            return redirect(post.get_absolute_url())

    return render(request, 'main/post_details.html', {
        'post': post,
        'comments': comments,
        'comment_form': comment_form,
    })
```

### 5.3 Додайте імпорт settings

На початку файлу додайте:

```python
from django.conf import settings
```

### 5.4 Додайте view для видалення коментаря

```python
@login_required
def comment_delete(request, id):
    comment = get_object_or_404(Comment, id=id)
    
    # Перевірка: тільки автор може видалити свій коментар
    if comment.author != request.user:
        return HttpResponseForbidden("Ви не маєте права видаляти цей коментар.")
    
    post = comment.post
    if request.method == 'POST':
        comment.delete()
        return redirect(post.get_absolute_url())
    
    return render(request, 'main/comment_confirm_delete.html', {
        'comment': comment,
    })
```

### Пояснення:

- **post_detail** — тепер обробляє і GET (показ поста + коментарі), і POST (додавання коментаря)
- **comment_form.save(commit=False)** — створює об'єкт коментаря, але не зберігає в БД, щоб ми могли додати `post` та `author`
- **redirect(post.get_absolute_url())** — після додавання коментаря перенаправляє назад на сторінку поста (PRG-патерн — Post/Redirect/Get)
- **comment_delete** — перевіряє, що тільки автор може видалити свій коментар

---

## Крок 6: Додавання URL маршрутів

**Файл:** `apps/main/urls.py`

Додайте два нові маршрути в `urlpatterns`:

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
    # Коментарі
    path('comment/<int:id>/delete/', views.comment_delete, name="comment_delete"),
]
```

---

## Крок 7: Оновлення шаблону post_details.html

**Файл:** `apps/main/templates/main/post_details.html`

Додайте блок коментарів **після** закриваючого тегу `</article>` і **перед** секцією "Схожі пости":

```html
<!-- Секція коментарів -->
<section class="mt-8 mb-8">
  <h2 class="text-2xl font-bold text-gray-800 mb-6">
    💬 Коментарі ({{ comments|length }})
  </h2>

  <!-- Форма додавання коментаря -->
  {% if user.is_authenticated %}
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h3 class="text-lg font-semibold text-gray-700 mb-4">Залишити коментар</h3>
    <form method="post" action="{% url 'main:post_detail' post.id post.slug %}">
      {% csrf_token %}
      <div class="mb-4">
        <label for="id_body" class="block text-sm font-medium text-gray-700 mb-2">
          {{ comment_form.body.label }}
        </label>
        {{ comment_form.body }}
        {% if comment_form.body.errors %}
          {% for error in comment_form.body.errors %}
            <p class="text-red-500 text-sm mt-1">{{ error }}</p>
          {% endfor %}
        {% endif %}
      </div>
      <button type="submit" class="bg-teal-600 hover:bg-teal-700 text-white px-6 py-2 rounded-lg transition-colors font-medium">
        Надіслати коментар
      </button>
    </form>
  </div>
  {% else %}
  <div class="bg-gray-50 rounded-lg p-6 mb-6 text-center">
    <p class="text-gray-600">
      Щоб залишити коментар, будь ласка,
      <a href="{% url 'accounts:login' %}?next={{ request.path }}" class="text-teal-600 hover:text-teal-700 font-medium underline">увійдіть</a>
      або
      <a href="{% url 'accounts:register' %}" class="text-teal-600 hover:text-teal-700 font-medium underline">зареєструйтесь</a>.
    </p>
  </div>
  {% endif %}

  <!-- Список коментарів -->
  {% if comments %}
    {% for comment in comments %}
    <div class="bg-white rounded-lg shadow-md p-6 mb-4">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
            <span class="text-teal-700 font-bold text-sm">{{ comment.author.username|first|upper }}</span>
          </div>
          <div>
            <p class="font-semibold text-gray-800">{{ comment.author.username }}</p>
            <p class="text-sm text-gray-500">{{ comment.created_at|date:"d.m.Y H:i" }}</p>
          </div>
        </div>
        {% if user == comment.author %}
        <form method="post" action="{% url 'main:comment_delete' comment.id %}" onsubmit="return confirm('Ви впевнені, що хочете видалити цей коментар?');">
          {% csrf_token %}
          <button type="submit" class="text-red-500 hover:text-red-700 text-sm font-medium transition-colors">
            🗑️ Видалити
          </button>
        </form>
        {% endif %}
      </div>
      <p class="text-gray-700 leading-relaxed">{{ comment.body|linebreaks }}</p>
    </div>
    {% endfor %}
  {% else %}
    <div class="bg-gray-50 rounded-lg p-6 text-center">
      <p class="text-gray-500">Поки що немає коментарів. Будьте першим!</p>
    </div>
  {% endif %}
</section>
```

### Повний оновлений шаблон post_details.html

Для зручності, ось як має виглядати повний файл:

```html
{% extends 'base.html' %}
{% load blog_filters %}
{% load blog_tags %}
{% block title %}{{ post.title }}{% endblock %}

{% block content %}
<article class="bg-white rounded-lg shadow-lg overflow-hidden mb-8">
  <div class="p-8">
    <h1 class="text-4xl font-bold text-gray-800 mb-4">{{ post.title }}</h1>
    <div class="flex flex-wrap gap-4 text-sm text-gray-500 mb-6 pb-6 border-b border-gray-200">
      <span>📖 Час читання: {{ post.content|reading_time }}</span>
      <span>🕒 Опубліковано: {{ post.created_at|time_ago }}</span>
      <span class="flex items-center gap-1">👁️ {{ post.views|compact_views }} переглядів</span>
      <span class="flex items-center gap-1">📂 <a href="{{ post.category.get_absolute_url }}" class="text-teal-600 hover:text-teal-700 font-medium">{{ post.category.name }}</a></span>
      {% if post.created_at|is_new %}
        <span class="badge badge-new">🆕 NEW!</span>
      {% endif %}
      <span>{{ post.likes|format_likes }}</span>
    </div>
    <p class="lead">{{ post.content|first_sentence }}</p>
  </div>

  {% if post.image %}
  <div class="w-full">
    <img src="{{ post.image.url }}" alt="{{ post.title }}" class="w-full max-h-96 object-cover">
  </div>
  {% endif %}

  <div class="p-8 prose prose-lg max-w-none">
    {{ post.content|linebreaks }}
  </div>

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
</article>

<!-- Секція коментарів -->
<section class="mt-8 mb-8">
  <h2 class="text-2xl font-bold text-gray-800 mb-6">
    💬 Коментарі ({{ comments|length }})
  </h2>

  {% if user.is_authenticated %}
  <div class="bg-white rounded-lg shadow-md p-6 mb-6">
    <h3 class="text-lg font-semibold text-gray-700 mb-4">Залишити коментар</h3>
    <form method="post" action="{% url 'main:post_detail' post.id post.slug %}">
      {% csrf_token %}
      <div class="mb-4">
        <label for="id_body" class="block text-sm font-medium text-gray-700 mb-2">
          {{ comment_form.body.label }}
        </label>
        {{ comment_form.body }}
        {% if comment_form.body.errors %}
          {% for error in comment_form.body.errors %}
            <p class="text-red-500 text-sm mt-1">{{ error }}</p>
          {% endfor %}
        {% endif %}
      </div>
      <button type="submit" class="bg-teal-600 hover:bg-teal-700 text-white px-6 py-2 rounded-lg transition-colors font-medium">
        Надіслати коментар
      </button>
    </form>
  </div>
  {% else %}
  <div class="bg-gray-50 rounded-lg p-6 mb-6 text-center">
    <p class="text-gray-600">
      Щоб залишити коментар, будь ласка,
      <a href="{% url 'accounts:login' %}?next={{ request.path }}" class="text-teal-600 hover:text-teal-700 font-medium underline">увійдіть</a>
      або
      <a href="{% url 'accounts:register' %}" class="text-teal-600 hover:text-teal-700 font-medium underline">зареєструйтесь</a>.
    </p>
  </div>
  {% endif %}

  {% if comments %}
    {% for comment in comments %}
    <div class="bg-white rounded-lg shadow-md p-6 mb-4">
      <div class="flex items-center justify-between mb-3">
        <div class="flex items-center gap-3">
          <div class="w-10 h-10 bg-teal-100 rounded-full flex items-center justify-center">
            <span class="text-teal-700 font-bold text-sm">{{ comment.author.username|first|upper }}</span>
          </div>
          <div>
            <p class="font-semibold text-gray-800">{{ comment.author.username }}</p>
            <p class="text-sm text-gray-500">{{ comment.created_at|date:"d.m.Y H:i" }}</p>
          </div>
        </div>
        {% if user == comment.author %}
        <form method="post" action="{% url 'main:comment_delete' comment.id %}" onsubmit="return confirm('Ви впевнені, що хочете видалити цей коментар?');">
          {% csrf_token %}
          <button type="submit" class="text-red-500 hover:text-red-700 text-sm font-medium transition-colors">
            🗑️ Видалити
          </button>
        </form>
        {% endif %}
      </div>
      <p class="text-gray-700 leading-relaxed">{{ comment.body|linebreaks }}</p>
    </div>
    {% endfor %}
  {% else %}
    <div class="bg-gray-50 rounded-lg p-6 text-center">
      <p class="text-gray-500">Поки що немає коментарів. Будьте першим!</p>
    </div>
  {% endif %}
</section>

{% get_related_posts post 4 as related_posts %}
{% if related_posts %}
<section class="mt-12">
  <h2 class="text-3xl font-bold text-gray-800 mb-6">Схожі пости</h2>
  <div class="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-3 gap-6">
    {% for related in related_posts %}
    <div class="bg-white rounded-lg shadow-md overflow-hidden hover:shadow-xl transition-shadow">
      {% if related.image %}
      <img src="{{ related.image.url }}" alt="{{ related.title }}" class="w-full h-40 object-cover">
      {% endif %}
      <div class="p-5">
        <h3 class="text-xl font-bold text-gray-800 mb-2 hover:text-teal-600 transition-colors">{{ related.title }}</h3>
        <p class="text-gray-600 mb-4 text-sm">{{ related.content|truncatewords:15 }}</p>
        <a href="{{ related.get_absolute_url }}" class="inline-block bg-teal-600 hover:bg-teal-700 text-white px-4 py-2 rounded-lg transition-colors font-medium text-sm">Читати далі →</a>
      </div>
    </div>
    {% endfor %}
  </div>
</section>
{% endif %}
{% endblock %}
```

---

## Крок 8: (Опціонально) Шаблон підтвердження видалення коментаря

**Файл:** `apps/main/templates/main/comment_confirm_delete.html`

Цей шаблон потрібен як fallback, якщо JavaScript `confirm()` не спрацює:

```html
{% extends 'base.html' %}
{% block title %}Видалити коментар{% endblock %}

{% block content %}
<div class="max-w-lg mx-auto mt-10">
  <div class="bg-white rounded-lg shadow-lg p-8">
    <h1 class="text-2xl font-bold text-gray-800 mb-4">Видалити коментар?</h1>
    <div class="bg-gray-50 rounded-lg p-4 mb-6">
      <p class="text-gray-700">{{ comment.body }}</p>
      <p class="text-sm text-gray-500 mt-2">— {{ comment.author.username }}, {{ comment.created_at|date:"d.m.Y H:i" }}</p>
    </div>
    <p class="text-gray-600 mb-6">Ви впевнені, що хочете видалити цей коментар? Цю дію не можна скасувати.</p>
    <div class="flex gap-4">
      <form method="post">
        {% csrf_token %}
        <button type="submit" class="bg-red-500 hover:bg-red-600 text-white px-6 py-2 rounded-lg transition-colors font-medium">
          Так, видалити
        </button>
      </form>
      <a href="{% url 'main:post_detail' comment.post.id comment.post.slug %}" class="bg-gray-100 hover:bg-gray-200 text-gray-700 px-6 py-2 rounded-lg transition-colors font-medium">
        Скасувати
      </a>
    </div>
  </div>
</div>
{% endblock %}
```

---

## Підсумок: Порядок дій

1. ✅ Додати модель `Comment` в `apps/main/models.py`
2. ✅ Виконати `python manage.py makemigrations main` та `python manage.py migrate`
3. ✅ Зареєструвати `Comment` в `apps/main/admin.py`
4. ✅ Додати `CommentForm` в `apps/main/forms.py`
5. ✅ Оновити `post_detail` та додати `comment_delete` в `apps/main/views.py`
6. ✅ Додати URL маршрут для видалення коментаря в `apps/main/urls.py`
7. ✅ Оновити шаблон `post_details.html` — додати секцію коментарів
8. ✅ (Опціонально) Створити шаблон `comment_confirm_delete.html`

## Перевірка роботи

1. Запустіть сервер: `python manage.py runserver`
2. Відкрийте будь-який пост
3. Якщо ви авторизовані — побачите форму для коментаря
4. Якщо ні — побачите посилання на вхід/реєстрацію
5. Залиште коментар і перевірте, що він з'явився
6. Натисніть "Видалити" біля свого коментаря
7. Перевірте адмін-панель: `/admin/` → Коментарі

## Можливі покращення

- **Редагування коментарів** — додати view `comment_update` з формою редагування
- **Відповіді на коментарі** — додати поле `parent = ForeignKey('self')` для вкладених коментарів
- **Лайки коментарів** — додати поле `likes` до моделі `Comment`
- **Пагінація коментарів** — якщо коментарів багато, розбити на сторінки
- **Модерація** — додати поле `is_approved` для перевірки коментарів перед публікацією
- **Сповіщення** — надсилати email автору поста, коли хтось залишає коментар
