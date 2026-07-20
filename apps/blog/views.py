
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.contrib.auth import get_user_model
from django.db.models import Q, Count
from django.core.paginator import Paginator
from django.utils import timezone

from apps.blog.forms import PostForm
from apps.blog.models import Post, Category, PostImage
from apps.comments.models import Comment
from apps.likes.models import Like
from apps.bookmarks.models import Bookmark

User = get_user_model()


def post_list_view(request):
    query = request.GET.get("q", "").strip()
    category_slug = request.GET.get("category", "").strip()
    tag_name = request.GET.get("tag", "").strip()

    posts = (
        Post.objects.filter(status="published")
        .select_related("user", "category")
        .prefetch_related("tags")
        .annotate(
            likes_count=Count("likes", distinct=True),
            comments_count=Count("comments", distinct=True),
        )
        .order_by("-published_at", "-created_at")
    )

    if query:
        posts = posts.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(user__username__icontains=query)
            | Q(user__full_name__icontains=query)
        )

    if category_slug:
        posts = posts.filter(category__slug=category_slug)

    if tag_name:
        posts = posts.filter(tags__name__iexact=tag_name)

    paginator = Paginator(posts.distinct(), 10)
    page_obj = paginator.get_page(request.GET.get("page"))

    context = {
        "posts": page_obj,
        "categories": Category.objects.all(),
        "query": query,
        "category_slug": category_slug,
        "tag_name": tag_name,
    }

    return render(request, "blog/post_list.html", context)


def post_detail_view(request, slug):
    post = get_object_or_404(
        Post.objects.select_related("user", "category").prefetch_related("tags"),
        slug=slug,
        status="published",
    )

    session_key = f"viewed_post_{post.id}"

    if not request.session.get(session_key):
        post.increment_views()
        request.session[session_key] = True

    comments = (
        Comment.objects.filter(
            post=post,
            parent=None,
            is_approved=True,
        )
        .select_related("user")
        .prefetch_related("replies")
        .order_by("-created_at")
    )

    related_posts = Post.objects.none()

    if post.category:
        related_posts = (
            Post.objects.filter(
                category=post.category,
                status="published",
            )
            .exclude(id=post.id)
            .select_related("user", "category")
            .order_by("-published_at", "-created_at")[:3]
        )

    is_liked = False
    is_bookmarked = False

    if request.user.is_authenticated:
        is_liked = Like.objects.filter(
            user=request.user,
            post=post,
        ).exists()

        is_bookmarked = Bookmark.objects.filter(
            user=request.user,
            post=post,
        ).exists()

    context = {
        "post": post,
        "comments": comments,
        "related_posts": related_posts,
        "is_liked": is_liked,
        "is_bookmarked": is_bookmarked,
    }

    return render(request, "blog/post_detail.html", context)


@login_required
def post_create_view(request):
    if request.method == "POST":
        form = PostForm(request.POST, request.FILES)

        if form.is_valid():
            post = form.save(commit=False)
            post.user = request.user
            post.save()

            form.save_m2m()

            for image in request.FILES.getlist("images"):
                PostImage.objects.create(
                    post=post,
                    image=image,
                )

            messages.success(request, "Post created successfully.")
            return redirect("post_detail", slug=post.slug)

    else:
        form = PostForm()

    return render(
        request,
        "blog/post_create.html",
        {
            "form": form,
            "title": "Create Post",
        },
    )


@login_required
def post_edit_view(request, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        user=request.user,
    )

    if request.method == "POST":
        form = PostForm(
            request.POST,
            request.FILES,
            instance=post,
        )

        if form.is_valid():
            form.save()

            for image in request.FILES.getlist("images"):
                PostImage.objects.create(
                    post=post,
                    image=image,
                )

            messages.success(request, "Post updated successfully.")
            return redirect("post_detail", slug=post.slug)

    else:
        form = PostForm(instance=post)

    return render(
        request,
        "blog/post_create.html",
        {
            "form": form,
            "title": "Edit Post",
        },
    )


@login_required
def post_delete_view(request, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        user=request.user,
    )

    if request.method == "POST":
        post.delete()
        messages.success(request, "Post deleted successfully.")
        return redirect("dashboard")

    return render(
        request,
        "blog/post_delete.html",
        {"post": post},
    )


@login_required
def draft_list_view(request):
    drafts = (
        Post.objects.filter(
            user=request.user,
            status="draft",
        )
        .order_by("-created_at")
    )

    return render(
        request,
        "blog/draft_list.html",
        {
            "drafts": drafts,
        },
    )


@login_required
def publish_draft_view(request, slug):
    post = get_object_or_404(
        Post,
        slug=slug,
        user=request.user,
        status="draft",
    )

    post.status = "published"
    post.published_at = timezone.now()
    post.save(update_fields=["status", "published_at"])

    messages.success(request, "Post published successfully.")

    return redirect(
        "post_detail",
        slug=post.slug,
    )


def search_view(request):
    query = request.GET.get("q", "").strip()
    tag = request.GET.get("tag", "").strip()

    results = (
        Post.objects.filter(status="published")
        .select_related("user", "category")
        .prefetch_related("tags")
    )

    if query:
        results = results.filter(
            Q(title__icontains=query)
            | Q(content__icontains=query)
            | Q(user__username__icontains=query)
            | Q(category__title__icontains=query)
            | Q(tags__name__icontains=query)
        )

    if tag:
        results = results.filter(tags__name__iexact=tag)

    context = {
        "query": query,
        "tag": tag,
        "results": results.distinct(),
    }

    return render(
        request,
        "search/search.html",
        context,
    )
