import logging
import random

from django.contrib.auth.tokens import default_token_generator
from django.utils.http import urlsafe_base64_encode, urlsafe_base64_decode
from django.utils.encoding import force_bytes, force_str
from django.core.mail import EmailMultiAlternatives
from django.template.loader import render_to_string
from django.conf import settings
from django.db.models import Sum, Count
from django.shortcuts import get_object_or_404

from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from drf_yasg.utils import swagger_auto_schema
from drf_yasg import openapi

from Blog import serializers as Blog_serializer
from Blog import models as Blog_models

logger = logging.getLogger(__name__)


# --------------------------------------------------------------------------
# Auth
# --------------------------------------------------------------------------
class MyTokenObtainPairView(TokenObtainPairView):
    serializer_class = Blog_serializer.MyTokenObtainPairSerializer


class RegisterView(generics.CreateAPIView):
    queryset = Blog_models.User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = Blog_serializer.RegisterSerializer


class ProfileView(generics.RetrieveUpdateAPIView):
    """Own profile only. User is derived from the token, never from the URL."""
    permission_classes = (IsAuthenticated,)
    serializer_class = Blog_serializer.ProfileSerializer

    def get_object(self):
        return self.request.user.profile


class ChangePasswordView(generics.UpdateAPIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = Blog_serializer.ChangePasswordSerializer

    def update(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = request.user
        if not user.check_password(serializer.validated_data['old_password']):
            return Response({"old_password": "Wrong password."},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({"message": "Password changed successfully."},
                        status=status.HTTP_200_OK)


def generate_numeric_otp(length=6):
    return ''.join([str(random.randint(0, 9)) for _ in range(length)])


class PasswordResetRequestView(generics.GenericAPIView):
    """Sends a signed, single-use reset link. No state stored on the user."""
    permission_classes = (AllowAny,)
    serializer_class = Blog_serializer.PasswordResetRequestSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        email = serializer.validated_data['email']
        user = Blog_models.User.objects.filter(email=email).first()
        # Always return 200 to avoid user enumeration.
        if user:
            uidb64 = urlsafe_base64_encode(force_bytes(user.pk))
            token = default_token_generator.make_token(user)
            link = (
                f"{settings.SITE_URL}/reset-password?"
                f"uidb64={uidb64}&token={token}"
            )
            merge_data = {'link': link, 'username': user.username}
            try:
                msg = EmailMultiAlternatives(
                    subject="Password Reset Request",
                    body=render_to_string("email/password_reset.txt", merge_data),
                    from_email=settings.DEFAULT_FROM_EMAIL,
                    to=[user.email],
                )
                msg.attach_alternative(
                    render_to_string("email/password_reset.html", merge_data),
                    "text/html")
                msg.send()
            except Exception as exc:  # pragma: no cover
                logger.error("Password reset email failed: %s", exc)
        return Response({"message": "If that email exists, a reset link was sent."})


class PasswordResetConfirmView(generics.GenericAPIView):
    permission_classes = (AllowAny,)
    serializer_class = Blog_serializer.PasswordResetConfirmSerializer

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        try:
            uid = force_str(urlsafe_base64_decode(serializer.validated_data['email']))
            user = Blog_models.User.objects.get(pk=uid)
        except (TypeError, ValueError, OverflowError, Blog_models.User.DoesNotExist):
            return Response({"message": "Invalid reset link."},
                            status=status.HTTP_400_BAD_REQUEST)
        token = serializer.validated_data['token']
        if not default_token_generator.check_token(user, token):
            return Response({"message": "Invalid or expired reset link."},
                            status=status.HTTP_400_BAD_REQUEST)
        user.set_password(serializer.validated_data['password'])
        user.save()
        return Response({"message": "Password reset successful."},
                        status=status.HTTP_200_OK)


# --------------------------------------------------------------------------
# Posts / Categories
# --------------------------------------------------------------------------
class CategoryListAPIView(generics.ListAPIView):
    serializer_class = Blog_serializer.CategorySerializer
    permission_classes = [AllowAny]
    queryset = Blog_models.Category.objects.all()


class PostCategoryListAPIView(generics.ListAPIView):
    serializer_class = Blog_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        category_slug = self.kwargs['category_slug']
        category = get_object_or_404(Blog_models.Category, slug=category_slug)
        return (Blog_models.Post.objects
                .filter(category=category, status="Active")
                .select_related('user', 'category')
                .prefetch_related('tags'))


class PostListAPIView(generics.ListAPIView):
    serializer_class = Blog_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return (Blog_models.Post.objects
                .filter(status="Active")
                .select_related('user', 'category')
                .prefetch_related('tags'))


class PostDetailAPIView(generics.RetrieveAPIView):
    serializer_class = Blog_serializer.PostSerializer
    permission_classes = [AllowAny]

    def get_object(self):
        slug = self.kwargs['slug']
        post = get_object_or_404(Blog_models.Post, slug=slug, status="Active")
        Blog_models.Post.objects.filter(pk=post.pk).update(view=post.view + 1)
        return post


class PostCreateAPIView(generics.CreateAPIView):
    serializer_class = Blog_serializer.PostSerializer
    permission_classes = [IsAuthenticated]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user,
                        profile=self.request.user.profile)


class PostEditAPIView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = Blog_serializer.PostSerializer
    permission_classes = [IsAuthenticated]
    lookup_field = 'pk'

    def get_queryset(self):
        # Ownership enforced: only the author's posts are visible/editable.
        return Blog_models.Post.objects.filter(user=self.request.user)


# --------------------------------------------------------------------------
# Social: like / bookmark / follow
# --------------------------------------------------------------------------
class LikePostAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'post_id': openapi.Schema(type=openapi.TYPE_INTEGER)}))
    def post(self, request):
        post = get_object_or_404(Blog_models.Post, id=request.data.get('post_id'))
        user = request.user
        if user in post.likes.all():
            post.likes.remove(user)
            return Response({"message": "Post Disliked"}, status=status.HTTP_200_OK)
        post.likes.add(user)
        Blog_models.Notification.objects.create(
            user=post.user, post=post, type="Like")
        return Response({"message": "Post Liked"}, status=status.HTTP_201_CREATED)


class BookmarkPostAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'post_id': openapi.Schema(type=openapi.TYPE_INTEGER)}))
    def post(self, request):
        post = get_object_or_404(Blog_models.Post, id=request.data.get('post_id'))
        user = request.user
        bookmark = Blog_models.Bookmark.objects.filter(post=post, user=user).first()
        if bookmark:
            bookmark.delete()
            return Response({"message": "Post Un-Bookmarked"},
                            status=status.HTTP_200_OK)
        Blog_models.Bookmark.objects.create(user=user, post=post)
        Blog_models.Notification.objects.create(
            user=post.user, post=post, type="Bookmark")
        return Response({"message": "Post Bookmarked"},
                        status=status.HTTP_201_CREATED)


class FollowAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'following_id': openapi.Schema(type=openapi.TYPE_INTEGER)}))
    def post(self, request):
        following_id = request.data.get('following_id')
        if not following_id:
            return Response({"message": "following_id required."},
                            status=status.HTTP_400_BAD_REQUEST)
        if int(following_id) == request.user.id:
            return Response({"message": "You cannot follow yourself"},
                            status=status.HTTP_400_BAD_REQUEST)
        following = get_object_or_404(Blog_models.User, id=following_id)
        follow = Blog_models.Follow.objects.filter(
            follower=request.user, following=following).first()
        if follow:
            follow.delete()
            return Response({"message": "Unfollowed", "following": False},
                            status=status.HTTP_200_OK)
        Blog_models.Follow.objects.create(
            follower=request.user, following=following)
        Blog_models.Notification.objects.create(
            user=following, type="Follow")
        return Response({"message": "Followed", "following": True},
                        status=status.HTTP_201_CREATED)


class FollowersListAPIView(generics.ListAPIView):
    serializer_class = Blog_serializer.FollowSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = get_object_or_404(Blog_models.User, id=self.kwargs['user_id'])
        return Blog_models.Follow.objects.filter(following=user).select_related(
            'follower', 'following')


class FollowingListAPIView(generics.ListAPIView):
    serializer_class = Blog_serializer.FollowSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        user = get_object_or_404(Blog_models.User, id=self.kwargs['user_id'])
        return Blog_models.Follow.objects.filter(follower=user).select_related(
            'follower', 'following')


# --------------------------------------------------------------------------
# Comments
# --------------------------------------------------------------------------
class PostCommentAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'post_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'comment': openapi.Schema(type=openapi.TYPE_STRING),
                'parent_id': openapi.Schema(type=openapi.TYPE_INTEGER),
            }))
    def post(self, request):
        post = get_object_or_404(Blog_models.Post, id=request.data.get('post_id'))
        parent = None
        parent_id = request.data.get('parent_id')
        if parent_id:
            parent = get_object_or_404(Blog_models.Comment, id=parent_id, post=post)
        comment = Blog_models.Comment.objects.create(
            post=post,
            parent=parent,
            user=request.user,
            name=request.user.full_name or request.user.username,
            email=request.user.email,
            comment=request.data.get('comment', ''),
        )
        Blog_models.Notification.objects.create(
            user=post.user, post=post, type="Comment")
        return Response({"message": "Comment submitted for moderation.",
                         "id": comment.id},
                        status=status.HTTP_201_CREATED)


# --------------------------------------------------------------------------
# Dashboard (owner-only)
# --------------------------------------------------------------------------
class DashboardStats(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = Blog_serializer.AuthorStatsSerializer

    def get(self, request, *args, **kwargs):
        user = request.user
        posts_qs = Blog_models.Post.objects.filter(user=user)
        stats = posts_qs.aggregate(
            views=Sum("view"), posts=Count("id"),
            likes=Count("likes"))
        followers = Blog_models.Follow.objects.filter(following=user).count()
        return Response({
            "views": stats["views"] or 0,
            "posts": stats["posts"] or 0,
            "likes": stats["likes"] or 0,
            "followers": followers,
        })


class DashboardPostLists(generics.ListAPIView):
    serializer_class = Blog_serializer.PostSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (Blog_models.Post.objects
                .filter(user=self.request.user)
                .select_related('category')
                .prefetch_related('tags'))


class DashboardCommentLists(generics.ListAPIView):
    """Comments on the authenticated author's posts only."""
    serializer_class = Blog_serializer.CommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return (Blog_models.Comment.objects
                .filter(post__user=self.request.user)
                .select_related('post', 'user'))


class DashboardNotificationLists(generics.ListAPIView):
    serializer_class = Blog_serializer.NotificationSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Blog_models.Notification.objects.filter(
            seen=False, user=self.request.user).select_related('post')


class DashboardMarkNotiSeenAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={'noti_id': openapi.Schema(type=openapi.TYPE_INTEGER)}))
    def post(self, request):
        noti = get_object_or_404(
            Blog_models.Notification, id=request.data.get('noti_id'),
            user=request.user)
        noti.seen = True
        noti.save()
        return Response({"message": "Notification marked as seen."})


class DashboardReplyCommentAPIView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    @swagger_auto_schema(
        request_body=openapi.Schema(
            type=openapi.TYPE_OBJECT,
            properties={
                'comment_id': openapi.Schema(type=openapi.TYPE_INTEGER),
                'reply': openapi.Schema(type=openapi.TYPE_STRING),
            }))
    def post(self, request):
        comment = get_object_or_404(
            Blog_models.Comment, id=request.data.get('comment_id'),
            post__user=request.user)
        comment.reply = request.data.get('reply', '')
        comment.save()
        return Response({"message": "Reply sent."})


class LogoutView(generics.GenericAPIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        try:
            token = RefreshToken(request.data.get('refresh'))
            token.blacklist()
        except Exception:
            pass
        return Response({"message": "Logged out."})


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    return Response({"status": "Blog API online."})
