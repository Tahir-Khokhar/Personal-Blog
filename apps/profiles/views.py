from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Count, Sum

from apps.profiles.forms import ProfileEditForm
from apps.profiles.models import Profile
from apps.blog.models import Post
from apps.follows.models import Follow
from apps.likes.models import Like
from apps.comments.models import Comment

User = get_user_model()


@login_required
def profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    return render(request, 'profiles/profile.html', {'profile': profile})


@login_required
def edit_profile_view(request):
    profile = get_object_or_404(Profile, user=request.user)
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=profile)
        if form.is_valid():
            form.save()
            messages.success(request, 'Profile updated successfully.')
            return redirect('profile')
    else:
        form = ProfileEditForm(instance=profile)
    return render(request, 'profiles/edit_profile.html', {'form': form, 'profile': profile})


def author_profile_view(request, username):
    user = get_object_or_404(User, username=username)
    profile = get_object_or_404(Profile, user=user)
    posts = Post.objects.filter(user=user, status='Active')[:10]
    is_following = False
    if request.user.is_authenticated:
        is_following = Follow.objects.filter(follower=request.user, following=user).exists()
    context = {
        'author': user,
        'profile': profile,
        'posts': posts,
        'is_following': is_following,
        'followers_count': profile.followers_count(),
        'following_count': profile.following_count(),
        'posts_count': profile.posts_count(),
    }
    return render(request, 'profiles/author_profile.html', context)
