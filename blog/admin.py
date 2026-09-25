from django.contrib import admin

from .models import (
    Post,
    Category,
    Comment,
    Profile
)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):

    list_display = (
        "name",
        "slug",
    )

    prepopulated_fields = {
        "slug": ("name",)
    }


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):

    list_display = (
        "title",
        "author",
        "category",
        "created_at",
    )

    prepopulated_fields = {
        "slug": ("title",)
    }

    search_fields = (
        "title",
        "content",
    )


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):

    list_display = (
        "post",
        "author",
        "created_at",
    )


@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):

    list_display = (
        "user",
        "bio",
    )