from django.shortcuts import render, get_object_or_404
from .models import Post, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q


def post_list(request, category_slug=None):
    posts = Post.objects.all()

    category = None
    search_query = None

    # Фільтрація по категорії
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = Post.objects.filter(category=category)

    # Пошук постів
    search_query = request.GET.get('q')
    if search_query:
        posts = posts.filter(
            Q(title__icontains=search_query) |
            Q(content__icontains=search_query) |
            Q(author__username__icontains=search_query)
        )

    sort = request.GET.get('sort')
    if sort == 'new':
        posts = posts.order_by('-created_at')
    elif sort == 'old':
        posts = posts.order_by('created_at')
    elif sort == 'popular':
        posts = posts.order_by('-views')

    # Пагінація
    paginator = Paginator(posts, 3)  # 6 постів на сторінку
    page = request.GET.get('page')

    try:
        posts = paginator.page(page)
    except PageNotAnInteger:
        # Якщо page не є числом, показуємо першу сторінку
        posts = paginator.page(1)
    except EmptyPage:
        # Якщо page виходить за межі, показуємо останню сторінку
        posts = paginator.page(paginator.num_pages)

    return render(request, 'main/post_list.html', {
        'posts': posts, 
        'category': category,
        'search_query': search_query,
    })

def post_detail(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    post.views += 1
    post.save()

    return render(request, 'main/post_details.html', {
        'post': post, 
    })