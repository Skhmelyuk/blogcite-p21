from django.shortcuts import render
from .models import Post, Category
from django.shortcuts import get_object_or_404

def post_list(request, category_slug=None):
    categories = Category.objects.all()
    posts = Post.objects.all()

    category = None

    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        posts = Post.objects.filter(category=category)

    sort = request.GET.get('sort')
    if sort == 'new':
        posts = posts.order_by('-created_at')
    elif sort == 'old':
        posts = posts.order_by('created_at')
    elif sort == 'popular':
        posts = posts.order_by('-views')

    return render(request, 'main/post_list.html', {
        'posts': posts, 
        'categories': categories, 
        'category': category
    })

def post_detail(request, id, slug):
    post = get_object_or_404(Post, id=id, slug=slug)
    post.views += 1
    post.save()

    related_posts = Post.objects.filter(category=post.category).exclude(id=post.id)[:4]

    return render(request, 'main/post_details.html', {
        'post': post, 
        'related_posts': related_posts
    })