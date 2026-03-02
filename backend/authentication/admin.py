from django.contrib import admin
from django.utils.html import format_html
from django.contrib.auth.admin import UserAdmin
from .models import User


@admin.register(User)
class CustomUserAdmin(UserAdmin):
    list_display = ("email", "username", "is_verified", "is_active", "is_staff")
    list_filter = ("is_verified", "is_active", "is_staff")
    search_fields = ("email", "username")
    readonly_fields = ("preview_large",)
    ordering = ("email",)
    fieldsets = (
        (None, {"fields": ("preview_large", "avatar", "email", "password")}),
        ("Personal info", {"fields": ("username", "first_name", "last_name")}),
        (
            "Permissions",
            {
                "fields": (
                    "is_active",
                    "is_staff",
                    "is_superuser",
                    "is_verified",
                    "groups",
                    "user_permissions",
                )
            },
        ),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    add_fieldsets = (
        (
            None,
            {
                "classes": ("wide",),
                "fields": ("email", "username", "password1", "password2"),
            },
        ),
    )
    
    def preview_large(self, obj):
        if obj.avatar:
            return format_html(
                '<img src="{}" style="max-height: 200px; border-radius: 10px;" />',
                obj.avatar.url,
            )
        return "Картинка не загружена"

    preview_large.short_description = "Предпросмотр"
