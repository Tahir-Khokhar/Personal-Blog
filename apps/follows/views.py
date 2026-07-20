from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse

from apps.follows.models import Follow
from apps.notifications.models import Notification
from apps.profiles.models import Profile


@login_required
def toggle_follow_view(request, username):
    user_to_follow = get_object_or_404(User, username=username)
    if user_to_follow == request.user:
        messages.error(request, 'You cannot follow yourself.')
        return redirect('author_profile', username=username)

    follow, created = Follow.objects.get_or_create(
        follower=request.user,
        following=user_to_follow
    )

    if not created:
        follow.delete()
        following = False
    else:
        following = True
        Notification.objects.create(
            user=user_to_follow,
            post=None,
            type='follow'
        )

    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'following': following})

    if following:
        messages.success(request, f'You are now following {user_to_follow.username}.')
    else:
        messages.info(request, f'You unfollowed {user_to_follow.username}.')
    return redirect('author_profile', username=username)


from django.contrib.auth import get_user_model
User = get_user_model()
