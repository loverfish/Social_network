from django.contrib import admin
from django.urls import include, path
# from django.contrib.auth.urls

urlpatterns = [
    path('', include('posts.urls')),
    path('auth/', include('users.urls')),
    path('auth/', include('django.contrib.auth.urls')),
    path('admin/', admin.site.urls),
]
