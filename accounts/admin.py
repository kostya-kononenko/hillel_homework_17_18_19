from django.contrib import admin
from django.contrib.auth import get_user_model
from django.contrib.auth.admin import UserAdmin
from .models import Post, Comment

User = get_user_model()


class PostInline(admin.StackedInline):
    model = Post
    extra = 1


class CommentInline(admin.StackedInline):
    model = Comment
    extra = 1


@admin.register(User)
class UserAdmin(UserAdmin):
    inlines = [PostInline, ]
    list_filter = ['username', 'last_name', ]
    search_fields = ['username', 'last_name']


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'short_description', 'full_description', 'image', 'published', 'data_post')
    inlines = [CommentInline, ]
    list_filter = ['title', 'author', 'data_post', 'published']
    search_fields = ['title', 'author']
    actions = ['comment_published']

    def comment_published(self, request, queryset):
        queryset.update(published=True)
    comment_published.short_description = "published"


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('username', 'text_comment', 'posts', 'published')
    list_filter = ['username', 'published', 'posts']
    search_fields = ['username', 'posts']
    actions = ['comment_published']

    def comment_published(self, request, queryset):
        queryset.update(published=True)
    comment_published.short_description = "published"
