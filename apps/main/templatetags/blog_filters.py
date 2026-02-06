from django import template
import re
from django.utils.html import strip_tags

register = template.Library()


# ФІЛЬТР 1: Час читання статті
@register.filter
def reading_time(text):
    text = re.sub(r'<[^>]+>', '', str(text))
    words = len(text.split())
    minutes = words / 200
    
    if minutes < 1:
        return "менше 1 хвилини"
    elif minutes < 2:
        return "1 хвилина"
    else:
        return f"{int(minutes)} хвилин"


# ФІЛЬТР 2: Компактне відображення чисел
@register.filter
def compact_views(value):
    try:
        value = int(value)
        if value >= 1000000:
            return f"{value / 1000000:.1f}M"
        elif value >= 1000:
            return f"{value / 1000:.1f}K"
        return str(value)
    except (ValueError, TypeError):
        return value


# ФІЛЬТР 3: Відносний час ("назад")
@register.filter
def time_ago(date):
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


# ФІЛЬТР 4: Скорочення тексту з трьома крапками
@register.filter
def truncate_words_custom(text, length=50):
    text = strip_tags(str(text))
    words = text.split()
    
    if len(words) <= length:
        return text
    
    return ' '.join(words[:length]) + '...'


# ФІЛЬТР 5: Форматування лайків
@register.filter
def format_likes(value):
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


# ФІЛЬТР 6: Перевірка чи пост новий (менше 7 днів)
@register.filter
def is_new(date):
    from django.utils import timezone
    from datetime import timedelta
    
    now = timezone.now()
    diff = now - date
    
    return diff < timedelta(days=7)


# ФІЛЬТР 7: Виділення першого речення
@register.filter
def first_sentence(text):
    text = strip_tags(str(text))
    
    for delimiter in ['. ', '! ', '? ']:
        if delimiter in text:
            return text.split(delimiter)[0] + delimiter.strip()
    
    return text[:100] + '...' if len(text) > 100 else text