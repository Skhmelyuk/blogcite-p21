from django import template
from apps.main.models import Post, Category
from django.db.models import Count

register = template.Library()


# ТЕГ 1: Кількість постів у категорії
@register.simple_tag
def posts_count_in_category(category):
    """
    Повертає кількість постів у категорії
    
    Використання: {% posts_count_in_category category %}
    """
    return Post.objects.filter(category=category).count()


# ТЕГ 2: Останні N постів
@register.simple_tag
def get_recent_posts(count=5):
    """
    Повертає останні N постів
    
    Використання: {% get_recent_posts 5 as recent_posts %}
    """
    return Post.objects.all().order_by('-created_at')[:count]


# ТЕГ 3: Найпопулярніші пости
@register.simple_tag
def get_popular_posts(count=5):
    """
    Повертає найпопулярніші пости за кількістю переглядів
    
    Використання: {% get_popular_posts 5 as popular_posts %}
    """
    return Post.objects.all().order_by('-views')[:count]


# ТЕГ 4: Категорії з кількістю постів
@register.simple_tag
def get_categories_with_count():
    """
    Повертає всі категорії з кількістю постів у кожній
    
    Використання: {% get_categories_with_count as categories %}
    """
    return Category.objects.annotate(
        posts_count=Count('post')
    ).filter(posts_count__gt=0)


# ТЕГ 5: Загальна кількість постів
@register.simple_tag
def total_posts_count():
    """
    Повертає загальну кількість постів
    
    Використання: {% total_posts_count %}
    """
    return Post.objects.count()


# ТЕГ 6: Загальна кількість переглядів
@register.simple_tag
def total_views_count():
    """
    Повертає загальну кількість переглядів всіх постів
    
    Використання: {% total_views_count %}
    """
    from django.db.models import Sum
    result = Post.objects.aggregate(total=Sum('views'))
    return result['total'] or 0


# ТЕГ 7: Пости того ж автора
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


# ТЕГ 8: Схожі пости (за категорією)
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


# ТЕГ 9: Перевірка чи є пости в категорії
@register.simple_tag
def has_posts_in_category(category):
    """
    Перевіряє чи є пости в категорії
    
    Використання: {% has_posts_in_category category as has_posts %}
    """
    return Post.objects.filter(category=category).exists()


# ТЕГ 10: Рандомний пост
@register.simple_tag
def get_random_post():
    """
    Повертає випадковий пост
    
    Використання: {% get_random_post as random_post %}
    """
    return Post.objects.order_by('?').first()

