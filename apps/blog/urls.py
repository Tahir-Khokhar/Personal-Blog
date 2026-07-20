from django.urls import path
from apps.blog import views as blog_views

urlpatterns = [
    path('', blog_views.post_list_view, name='post_list'),
    path('post/create/', blog_views.post_create_view, name='post_create'),
    path('post/<slug:slug>/', blog_views.post_detail_view, name='post_detail'),
    path('post/<slug:slug>/edit/', blog_views.post_edit_view, name='post_edit'),
    path('post/<slug:slug>/delete/', blog_views.post_delete_view, name='post_delete'),
    path('drafts/', blog_views.draft_list_view, name='draft_list'),
    path('drafts/<slug:slug>/publish/', blog_views.publish_draft_view, name='publish_draft'),
    path('search/', blog_views.search_view, name='search'),
]



