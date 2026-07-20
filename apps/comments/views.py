from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse, HttpResponseForbidden

from apps.comments.forms import CommentForm
from apps.comments.models import Comment
from apps.blog.models import Post
from apps.notifications.models import Notification


def add_comment_view(request, slug):
    post = get_object_or_404(Post, slug=slug, status='published')
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = post
            comment.user = request.user if request.user.is_authenticated else None
            comment.name = request.user.full_name or request.user.username if request.user.is_authenticated else 'Anonymous'
            comment.email = request.user.email if request.user.is_authenticated else ''
            comment.is_approved = True
            comment.save()

            post.increment_comments()

            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    post=post,
                    type='comment'
                )

            messages.success(request, 'Comment added successfully.')
            return redirect('post_detail', slug=slug)
    return redirect('post_detail', slug=slug)


@login_required
def edit_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    if request.method == 'POST':
        new_text = request.POST.get('comment', '').strip()
        if new_text:
            comment.comment = new_text
            comment.save()
            messages.success(request, 'Comment updated successfully.')
        else:
            messages.error(request, 'Comment cannot be empty.')
    return redirect('post_detail', slug=comment.post.slug)


@login_required
def delete_comment_view(request, comment_id):
    comment = get_object_or_404(Comment, id=comment_id, user=request.user)
    post = comment.post
    if request.method == 'POST':
        post.decrement_comments()
        comment.delete()
        messages.success(request, 'Comment deleted successfully.')
    return redirect('post_detail', slug=post.slug)


@login_required
def reply_comment_view(request, comment_id):
    parent_comment = get_object_or_404(Comment, id=comment_id)
    post = parent_comment.post

    if request.method == 'POST':
        reply_text = request.POST.get('reply', '').strip()
        if reply_text:
            reply = Comment.objects.create(
                post=post,
                parent=parent_comment,
                user=request.user,
                name=request.user.full_name or request.user.username,
                email=request.user.email,
                comment=reply_text,
                is_approved=True,
            )

            if post.user != request.user:
                Notification.objects.create(
                    user=post.user,
                    post=post,
                    type='reply'
                )

            messages.success(request, 'Reply added successfully.')
        else:
            messages.error(request, 'Reply cannot be empty.')
    return redirect('post_detail', slug=post.slug)
