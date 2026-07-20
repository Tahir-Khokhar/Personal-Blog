from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.bookmarks.models import Bookmark
from apps.blog.models import Post


@login_required
def toggle_bookmark_view(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    bookmark, created = Bookmark.objects.get_or_create(user=request.user, post=post)

    if not created:
        bookmark.delete()
        bookmarked = False
    else:
        bookmarked = True
        if post.user != request.user:
            from apps.notifications.models import Notification
            Notification.objects.create(
                user=post.user,
                post=post,
                type='bookmark'
            )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'bookmarked': bookmarked})

    if bookmarked:
        messages.success(request, 'Post saved to bookmarks.')
    else:
        messages.info(request, 'Post removed from bookmarks.')
    return redirect('post_detail', slug=slug)


@login_required
def bookmark_list_view(request):
    bookmarks = Bookmark.objects.filter(user=request.user).select_related('post')
    return render(request, 'bookmarks/bookmark_list.html', {'bookmarks': bookmarks})
