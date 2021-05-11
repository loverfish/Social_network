from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('author/<str:username>/', profile, name='profile'),
    path('author/<str:username>/<int:post_id>', post_view, name='post'),
    path('author/<str:username>/<int:post_id>/edit', post_edit, name='post_edit'),
    path('author/<str:username>/<int:post_id>/comment', add_comment, name='add_comment'),
    path('group/<slug>/', group_posts, name='group_posts'),
    path('new/', new_post, name='new_post'),
    path('follow/', follow_index, name="follow_index"),
    path('followers/', followers_index, name="followers_index"),
    path('follow/<str:username>/', profile_follow, name="profile_follow"),
    path('unfollow/<str:username>/', profile_unfollow, name="profile_unfollow"),
    path('404/', page_not_found),
    path('500/', server_error),

]
