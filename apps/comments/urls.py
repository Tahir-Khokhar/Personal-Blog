from django.urls import path
from apps.comments import views as comments_views

urlpatterns = [
    path('post/<slug:slug>/comment/', comments_views.add_comment_view, name='add_comment'),
    path('comment/<int:comment_id>/edit/', comments_views.edit_comment_view, name='edit_comment'),
    path('comment/<int:comment_id>/delete/', comments_views.delete_comment_view, name='delete_comment'),
    path('comment/<int:comment_id>/reply/', comments_views.reply_comment_view, name='reply_comment'),
]
