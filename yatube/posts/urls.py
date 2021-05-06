from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('author/<str:username>/', profile, name='profile'),
    path('author/<str:username>/<int:post_id>', post_view, name='post'),
    path('author/<str:username>/<int:post_id>/edit', post_edit, name='post_edit'),
    path('new/', new_post, name='new_post'),
    path('group/<slug>/', group_posts, name='group_posts'),
    path('404/', page_not_found),
    path('500/', server_error),

]
