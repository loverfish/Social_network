from django.urls import path

from .views import *

urlpatterns = [
    path('', index, name='index'),
    path('new/', new_post, name='new_post'),
    path('group/<slug>/', group_posts, name='group_posts'),

]
