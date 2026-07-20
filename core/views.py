from django.shortcuts import render


def home_view(request):
    from apps.blog.models import Post
    from apps.blog.models import Category

    latest_posts = Post.objects.filter(status='published').select_related('user', 'category').prefetch_related('tags')[:6]
    categories = Category.objects.all()[:8]

    context = {
        'latest_posts': latest_posts,
        'categories': categories,
    }
    return render(request, 'home.html', context)
