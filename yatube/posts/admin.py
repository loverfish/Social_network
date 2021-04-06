from django.contrib import admin

from .models import Post


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    empty_value_display = ('-empty-',)


admin.site.register(Post, PostAdmin)
