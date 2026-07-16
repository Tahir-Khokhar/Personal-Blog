from django.urls import path
from rest_framework_simplejwt.views import TokenRefreshView
from Blog import views as Blog_views

urlpatterns = [
    # Userauths API Endpoints
    path('user/token/', Blog_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', Blog_views.RegisterView.as_view(), name='auth_register'),
    path('user/profile/<user_id>/', Blog_views.ProfileView.as_view(), name='user_profile'),
    path('user/password-reset/<email>/', Blog_views.PasswordEmailVerify.as_view(), name='password_reset'),
    path('user/password-change/', Blog_views.PasswordChangeView.as_view(), name='password_reset'),

    # Post Endpoints
    path('post/category/list/', Blog_views.CategoryListAPIView.as_view()),
    path('post/category/posts/<category_slug>/', Blog_views.PostCategoryListAPIView.as_view()),
    path('post/lists/', Blog_views.PostListAPIView.as_view()),
    path('post/detail/<slug>/', Blog_views.PostDetailAPIView.as_view()),
    path('post/like-post/', Blog_views.LikePostAPIView.as_view()),
    path('post/comment-post/', Blog_views.PostCommentAPIView.as_view()),
    path('post/bookmark-post/', Blog_views.BookmarkPostAPIView.as_view()),

    # Dashboard APIS
    path('author/dashboard/stats/<user_id>/', Blog_views.DashboardStats.as_view()),
    path('author/dashboard/post-list/<user_id>/', Blog_views.DashboardPostLists.as_view()),
    path('author/dashboard/comment-list/', Blog_views.DashboardCommentLists.as_view()),
    path('author/dashboard/noti-list/<user_id>/', Blog_views.DashboardNotificationLists.as_view()),
    path('author/dashboard/noti-mark-seen/', Blog_views.DashboardMarkNotiSeenAPIView.as_view()),
    path('author/dashboard/reply-comment/', Blog_views.DashboardPostCommentAPIView.as_view()),
    path('author/dashboard/post-create/', Blog_views.DashboardPostCreateAPIView.as_view()),
    path('author/dashboard/post-detail/<user_id>/<post_id>/', Blog_views.DashboardPostEditAPIView.as_view()),


]
