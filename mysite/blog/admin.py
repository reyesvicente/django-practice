from django.contrib.admin import register, ModelAdmin
from .models import Post, Comment


@register(Comment)
class CommentAdmin(ModelAdmin):
    list_display = ('name', 'email', 'post', 'created', 'active')
    list_filter = ('active', 'created', 'updated',)
    search_fields = ('name', 'email', 'body',)

@register(Post)
class PostAdmin(ModelAdmin):
    list_display = ('title', 'slug', 'author', 'publish', 'status')
    list_filter = ('status', 'created', 'publish', 'author')
    search_fields = ('title', 'body')
    prepopulated_fields = {'slug': ('title',)}
    raw_id_fields = ('author',)
    date_hierarchy = 'publish'
    ordering = ('status', 'publish')