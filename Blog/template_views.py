from __future__ import annotations

import hashlib
import secrets
from datetime import datetime, timezone as dt_timezone

from django.conf import settings
from django.contrib import messages
from django.contrib.auth import authenticate, get_user_model, login, logout
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.views import PasswordChangeView
from django.http import Http404, HttpRequest, HttpResponse, HttpResponseBadRequest, JsonResponse
from django.shortcuts import get_object_or_404, redirect
from django.urls import reverse, reverse_lazy
from django.utils import timezone
from django.utils.decorators import method_decorator
from django.views import View
from django.views.decorators.csrf import csrf_protect
from django.views.generic import CreateView, DeleteView, DetailView, ListView, UpdateView
from django.views.generic.base import TemplateView

from Blog.forms import CommentForm, PostForm, SubscriptionForm
from Blog.models import (
    Bookmark,
    Category,
    Comment,
    EmailSubscription,
    Follow,
    Notification,
    Post,
    Profile,
)

User = get_user_model()


# ----------------------------- Public views -----------------------------

class PostListView(ListView):
    model = Post
    template_name = 'blog/post_list.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(status="Active")
            .select_related('user', 'category')
            .prefetch_related('tags')
            .order_by('-date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['categories'] = Category.objects.all()
        return context


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/post_detail.html'
    context_object_name = 'post'
    slug_url_kwarg = 'slug'

    def get_queryset(self):
        # Hide non-active posts even if URL is known.
        return Post.objects.filter(status="Active")

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['comments'] = (
            self.object.comments()
            .filter(is_approved=True)
            .select_related('user')
        )
        context['form'] = CommentForm()
        context['related_posts'] = (
            Post.objects.filter(category=self.object.category, status="Active")
            .exclude(id=self.object.id)[:3]
        )
        context['is_liked'] = False
        context['is_bookmarked'] = False
        if self.request.user.is_authenticated:
            context['is_liked'] = self.object.likes.filter(id=self.request.user.id).exists()
            context['is_bookmarked'] = Bookmark.objects.filter(user=self.request.user, post=self.object).exists()
        return context

    def post(self, request: HttpRequest, *args, **kwargs):
        if not request.user.is_authenticated:
            messages.error(request, 'Please log in to comment.')
            return redirect('login')

        self.object = self.get_object()
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.post = self.object
            comment.user = request.user
            comment.name = request.user.full_name or request.user.username
            comment.email = request.user.email

            # For production: either approve immediately for logged-in users or keep moderation.
            # Here: approve if user is authenticated; otherwise it's already blocked.
            comment.is_approved = True
            comment.save()
            Notification.objects.create(user=self.object.user, post=self.object, type="Comment")
            return redirect(reverse('post_detail', kwargs={'slug': self.object.slug}))

        context = self.get_context_data(form=form)
        return self.render_to_response(context)


class CategoryPostListView(ListView):
    model = Post
    template_name = 'blog/category_posts.html'
    context_object_name = 'posts'
    paginate_by = 10

    def get_queryset(self):
        return (
            Post.objects.filter(category__slug=self.kwargs['category_slug'], status="Active")
            .select_related('user', 'category')
            .order_by('-date')
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category'] = get_object_or_404(Category, slug=self.kwargs['category_slug'])
        context['categories'] = Category.objects.all()
        return context


# ----------------------------- Auth UI views -----------------------------

class RegisterView(CreateView):
    model = User
    template_name = 'auth/register.html'
    fields = ['full_name', 'email']

    def post(self, request: HttpRequest, *args, **kwargs):
        full_name = (request.POST.get('full_name') or '').strip()
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password')
        password2 = request.POST.get('password2')

        if not email or not password or not password2:
            messages.error(request, 'Please fill in all required fields.')
            return redirect('register')

        if password != password2:
            messages.error(request, 'Passwords do not match.')
            return redirect('register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email is already registered.')
            return redirect('register')

        user = User.objects.create_user(email=email, full_name=full_name, password=password)
        # Ensure profile created by signal.
        login(request, user)
        messages.success(request, 'Account created successfully.')
        return redirect('dashboard')


class LoginView(TemplateView):
    template_name = 'auth/login.html'

    def get(self, request: HttpRequest, *args, **kwargs):
        return super().get(request, *args, **kwargs)

    def post(self, request: HttpRequest, *args, **kwargs):
        email = (request.POST.get('email') or '').strip().lower()
        password = request.POST.get('password')
        user = authenticate(request, username=email, password=password)
        if user is None:
            messages.error(request, 'Invalid email or password.')
            return redirect('login')
        login(request, user)
        return redirect('dashboard')


class LogoutView(View):
    def post(self, request: HttpRequest, *args, **kwargs):
        logout(request)
        return redirect('home')

    def get(self, request: HttpRequest, *args, **kwargs):
        logout(request)
        return redirect('home')


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = Profile
    template_name = 'auth/edit_profile.html'
    fields = ['image', 'full_name', 'bio', 'about', 'country', 'facebook', 'twitter']

    def get_object(self, queryset=None):
        return get_object_or_404(Profile, user=self.request.user)

    def form_valid(self, form):
        messages.success(self.request, 'Profile updated successfully.')
        return super().form_valid(form)

    def get_success_url(self):
        return reverse('dashboard')


class AccountSettingsView(LoginRequiredMixin, View):
    template_name = 'auth/settings.html'

    def get(self, request: HttpRequest):
        profile = get_object_or_404(Profile, user=request.user)
        return self.render_to_response({'profile': profile})


class PasswordChangeView(LoginRequiredMixin, View):
    template_name = 'auth/password_change.html'

    def get(self, request: HttpRequest):
        return self.render_to_response({})

    def post(self, request: HttpRequest):
        # Simple production-ready password change using Django auth form.
        from django.contrib.auth.forms import PasswordChangeForm

        form = PasswordChangeForm(user=request.user, data=request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Password changed successfully.')
            return redirect('settings')
        messages.error(request, 'Please correct the errors below.')
        return self.render_to_response({'form': form})


# ----------------------------- Authoring views -----------------------------

class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        form.instance.user = self.request.user
        form.instance.profile = self.request.user.profile
        response = super().form_valid(form)
        if self.object.status == "Active":
            from Blog.models import send_new_post_email
            send_new_post_email(self.object)
        return response


class PostEditView(LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/post_create.html'

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, slug=self.kwargs['slug'])
        if obj.user_id != self.request.user.id:
            raise Http404('Not found')
        return obj

    def get_success_url(self):
        return reverse('post_detail', kwargs={'slug': self.object.slug})


class PostDeleteView(LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/post_confirm_delete.html'
    success_url = reverse_lazy('dashboard_posts')

    def get_object(self, queryset=None):
        obj = get_object_or_404(Post, slug=self.kwargs['slug'])
        if obj.user_id != self.request.user.id:
            raise Http404('Not found')
        return obj


class SubscriptionView(CreateView):
    model = EmailSubscription
    form_class = SubscriptionForm
    template_name = 'blog/subscribe.html'
    success_url = reverse_lazy('home')

    def form_valid(self, form):
        # Avoid duplicates.
        email = form.cleaned_data['email'].lower()
        EmailSubscription.objects.update_or_create(email=email, defaults={'is_active': True})
        messages.success(self.request, 'Subscribed successfully.')
        return redirect(self.get_success_url())


class UnsubscribeView(LoginRequiredMixin, View):
    template_name = 'blog/unsubscribe.html'


# ----------------------------- SEO / other feed -----------------------------

from django.contrib.syndication.views import Feed


class LatestPostsFeed(Feed):
    title = "Latest Posts"
    link = reverse_lazy('home')
    description = "Updates on new blog posts"

    def items(self):
        return Post.objects.filter(status="Active").order_by('-date')[:10]

    def item_title(self, item):
        return item.title

    def item_description(self, item):
        return item.description

    def item_link(self, item):
        return reverse('post_detail', kwargs={'slug': item.slug})


# ----------------------------- Dashboard stubs (to be completed next) -----------------------------

class DashboardView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/dashboard.html'

    def get_context_data(self, **kwargs):
        return super().get_context_data(**kwargs)


class NotificationsView(LoginRequiredMixin, TemplateView):
    template_name = 'dashboard/notifications.html'


class DashboardPostsView(LoginRequiredMixin, ListView):
    model = Post
    template_name = 'dashboard/posts.html'
    context_object_name = 'posts'

    def get_queryset(self):
        return Post.objects.filter(user=self.request.user).order_by('-date')


class DashboardCommentsView(LoginRequiredMixin, ListView):
    model = Comment
    template_name = 'dashboard/comments.html'
    context_object_name = 'comments'

    def get_queryset(self):
        return Comment.objects.filter(user=self.request.user).order_by('-date')


# ----------------------------- AJAX endpoints (like/bookmark/follow/comment) -----------------------------
# Next tasks will fully implement, for now keep safe stubs.

class LikeToggleAPIView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        return JsonResponse({"detail": "Not implemented yet"}, status=501)


class BookmarkToggleAPIView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        return JsonResponse({"detail": "Not implemented yet"}, status=501)


class FollowToggleAPIView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        return JsonResponse({"detail": "Not implemented yet"}, status=501)


class CommentCreateAPIView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        return JsonResponse({"detail": "Not implemented yet"}, status=501)


class CommentDeleteAPIView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        return JsonResponse({"detail": "Not implemented yet"}, status=501)


class CommentEditAPIView(LoginRequiredMixin, View):
    def post(self, request: HttpRequest):
        return JsonResponse({"detail": "Not implemented yet"}, status=501)


# ----------------------------- Remaining list/search/archive stubs -----------------------------

class TagPostListView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/tag_posts.html'


class SearchPostsView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/search_posts.html'


class ArchiveView(LoginRequiredMixin, TemplateView):
    template_name = 'blog/archive.html'


class AuthorProfileView(DetailView):
    model = User
    template_name = 'profiles/author_profile.html'
    context_object_name = 'author'

