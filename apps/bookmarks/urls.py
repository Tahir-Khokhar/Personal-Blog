from django.urls import path
from apps.bookmarks import views as bookmarks_views

urlpatterns = [
    path('post/<slug:slug>/bookmark/', bookmarks_views.toggle_bookmark_view, name='toggle_bookmark'),
    path('saved/', bookmarks_views.bookmark_list_view, name='bookmark_list'),
]
