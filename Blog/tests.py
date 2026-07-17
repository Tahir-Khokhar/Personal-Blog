from django.urls import path  # Import URL routing function.
from rest_framework_simplejwt.views import TokenRefreshView  # Import JWT token refresh view.
from Blog import views as Blog_views  # Import API views.
from Blog import template_views  # Import template-based views.
from Blog import feeds as Blog_feeds  # Import RSS feed.
from django.contrib.sitemaps.views import sitemap  # Import sitemap view.
from Blog.sitemap import PostSitemap, CategorySitemap  # Import sitemap classes.

# Register available sitemaps.
sitemaps = {
    'posts': PostSitemap,
    'categories': CategorySitemap,
}

# Define all application URL routes.
urlpatterns = [

    # Authentication routes.
    path('user/token/', Blog_views.MyTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('user/token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('user/register/', Blog_views.RegisterView.as_view(), name='auth_register'),
    path('user/profile/', Blog_views.ProfileView.as_view(), name='user_profile'),
    path('user/change-password/', Blog_views.ChangePasswordView.as_view(), name='change_password'),
    path('user/logout/', Blog_views.LogoutView.as_view(), name='logout'),
    path('user/password-reset/', Blog_views.PasswordResetRequestView.as_view(), name='password_reset_request'),
    path('user/password-reset/confirm/', Blog_views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),

    # Blog post routes.
    path('post/category/list/', Blog_views.CategoryListAPIView.as_view()),
    path('post/category/posts/<category_slug>/', Blog_views.PostCategoryListAPIView.as_view()),
    path('post/lists/', Blog_views.PostListAPIView.as_view()),
    path('post/detail/<slug>/', Blog_views.PostDetailAPIView.as_view()),
    path('post/create/', Blog_views.PostCreateAPIView.as_view()),
    path('post/<int:pk>/', Blog_views.PostEditAPIView.as_view()),
    path('post/like-post/', Blog_views.LikePostAPIView.as_view()),
    path('post/comment-post/', Blog_views.PostCommentAPIView.as_view()),
    path('post/bookmark-post/', Blog_views.BookmarkPostAPIView.as_view()),

    # Follow system routes.
    path('user/follow/', Blog_views.FollowAPIView.as_view()),
    path('user/followers/<user_id>/', Blog_views.FollowersListAPIView.as_view()),
    path('user/following/<user_id>/', Blog_views.FollowingListAPIView.as_view()),

    # Author dashboard routes.
    path('author/dashboard/stats/', Blog_views.DashboardStats.as_view()),
    path('author/dashboard/post-list/', Blog_views.DashboardPostLists.as_view()),
    path('author/dashboard/comment-list/', Blog_views.DashboardCommentLists.as_view()),
    path('author/dashboard/noti-list/', Blog_views.DashboardNotificationLists.as_view()),
    path('author/dashboard/noti-mark-seen/', Blog_views.DashboardMarkNotiSeenAPIView.as_view()),
    path('author/dashboard/reply-comment/', Blog_views.DashboardReplyCommentAPIView.as_view()),

    # Template-based web page routes.
    path('', template_views.PostListView.as_view(), name='home'),
    path('post/<slug>/', template_views.PostDetailView.as_view(), name='post_detail'),
    path('category/<category_slug>/', template_views.CategoryPostListView.as_view(), name='category_posts'),
    path('post/create/', template_views.PostCreateView.as_view(), name='post_create'),
    path('subscribe/', template_views.SubscriptionView.as_view(), name='subscribe'),

    # RSS feed route.
    path('feed/', Blog_feeds.LatestPostsFeed(), name='feed'),

    # XML sitemap route.
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps}, name='sitemap'),
]
