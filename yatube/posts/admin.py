from django.contrib import admin

from .models import Post, Group, Comment


class PostAdmin(admin.ModelAdmin):
    list_display = ('pk', 'text', 'pub_date', 'author', 'group')
    list_filter = ('pub_date',)
    search_fields = ('text',)
    empty_value_display = '-empty-'


class GroupAdmin(admin.ModelAdmin):
    list_display = ("pk", "description", "title", "slug")
    search_fields = ("description", "title")
    empty_value_display = "-пусто-"



class CommentAdmin(admin.ModelAdmin):
    list_display = ("pk", "text", "author", "post", 'created')
    list_filter = ('created',)
    search_fields = ('text', 'post__text', 'author__username')
    empty_value_display = "-пусто-"


admin.site.register(Post, PostAdmin)
admin.site.register(Group, GroupAdmin)
admin.site.register(Comment, CommentAdmin)
