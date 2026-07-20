from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.db.models import Count, Sum, Q

from apps.blog.models import Post
from apps.profiles.models import Profile
from apps.follows.models import Follow
from apps.likes.models import Like
from apps.comments.models import Comment
from apps.notifications.models import Notification


@login_required
def dashboard_view(request):
    profile = Profile.objects.get(user=request.user)

    stats = {
        'total_posts': Post.objects.filter(user=request.user).count(),
        'published_posts': Post.objects.filter(user=request.user, status='published').count(),
        'total_views': Post.objects.filter(user=request.user).aggregate(total=Sum('views'))['total'] or 0,
        'total_likes': Like.objects.filter(post__user=request.user).count(),
        'total_comments': Comment.objects.filter(post__user=request.user).count(),
        'followers_count': Follow.objects.filter(following=request.user).count(),
        'following_count': Follow.objects.filter(follower=request.user).count(),
    }

    recent_posts = Post.objects.filter(user=request.user).order_by('-created_at')[:5]
    recent_comments = Comment.objects.filter(post__user=request.user).order_by('-created_at')[:5]
    unread_notifications = Notification.objects.filter(user=request.user, is_read=False)[:5]

    context = {
        'profile': profile,
        'stats': stats,
        'recent_posts': recent_posts,
        'recent_comments': recent_comments,
        'unread_notifications': unread_notifications,
    }
    return render(request, 'dashboard/dashboard.html', context)


@login_required
def dashboard_posts_view(request):
    posts = Post.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/posts.html', {'posts': posts})


@login_required
def dashboard_comments_view(request):
    comments = Comment.objects.filter(post__user=request.user).select_related('post', 'user').order_by('-created_at')
    return render(request, 'dashboard/comments.html', {'comments': comments})


@login_required
def dashboard_notifications_view(request):
    notifications = Notification.objects.filter(user=request.user).order_by('-created_at')
    return render(request, 'dashboard/notifications.html', {'notifications': notifications})
