from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.likes.models import Like
from apps.blog.models import Post
from apps.notifications.models import Notification


@login_required
def toggle_like_view(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    like, created = Like.objects.get_or_create(user=request.user, post=post)

    if not created:
        like.delete()
        post.decrement_likes()
        liked = False
    else:
        post.increment_likes()
        liked = True
        if post.user != request.user:
            Notification.objects.create(
                user=post.user,
                post=post,
                type='like'
            )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'liked': liked, 'likes_count': post.likes_count})

    if liked:
        messages.success(request, 'Post liked.')
    else:
        messages.info(request, 'Post unliked.')
    return redirect('post_detail', slug=slug)
