from django.shortcuts import render, get_object_or_404, redirect
from .models import Post, Category
from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.db.models import Q
from django.contrib.auth.decorators import login_required
from django.http import HttpResponseForbidden
from .forms import PostForm


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