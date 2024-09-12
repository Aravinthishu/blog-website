from django.contrib import admin
from .models import *
from tinymce.widgets import TinyMCE
from django.db import models

class CategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    search_fields = ('name',)
    prepopulated_fields = {'slug': ('name',)}

admin.site.register(Category, CategoryAdmin)


class BlogPostAdmin(admin.ModelAdmin):
    list_display = ('title', 'author', 'created_at', 'updated_at', 'is_published')
    list_filter = ('is_published', 'created_at', 'updated_at', 'categories')  # Add categories to filters
    search_fields = ('title', 'slug', 'author__username', 'short_description', 'long_description')
    prepopulated_fields = {"slug": ("title",)}
    formfield_overrides = {
        models.TextField: {'widget': TinyMCE()},
    }

    fieldsets = (
        (None, {
            'fields': ('title', 'slug', 'author', 'categories', 'short_description', 'long_description', 'main_image', 'thumbnail', 'is_published')
        }),
        ('Dates', {
            'fields': ('created_at', 'updated_at', 'published_at'),
            'classes': ('collapse',),
        }),
    )

    readonly_fields = ('created_at', 'updated_at')
    filter_horizontal = ('categories',)  # Use horizontal filter widget for categories
    
class CommentAdmin(admin.ModelAdmin):
    list_display = ('blog_post', 'user', 'created_at', 'is_active')
    search_fields = ('user__username', 'content')
    list_filter = ('is_active', 'created_at')
    readonly_fields = ('created_at', 'updated_at')

class ReplyAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'created_at')
    search_fields = ('user__username', 'content')
    list_filter = ('created_at',)
    readonly_fields = ('created_at', 'updated_at')

class CommentLikeAdmin(admin.ModelAdmin):
    list_display = ('comment', 'user', 'liked_at')
    search_fields = ('user__username',)
    list_filter = ('liked_at',)

admin.site.register(BlogPost, BlogPostAdmin)
admin.site.register(Contact)
admin.site.register(Comment, CommentAdmin)
admin.site.register(Reply, ReplyAdmin)
admin.site.register(CommentLike, CommentLikeAdmin)

@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    pass

