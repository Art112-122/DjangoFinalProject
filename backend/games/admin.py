from django.contrib import admin
from django.utils.html import format_html
from .models import Game, Service


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    classes = ("collapse",)
    readonly_fields = ("preview_small",)
    fields = ("preview_small", "title", "price", "author")

    def preview_small(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 30px; height: 20px; object-fit: cover;"/>',
                obj.image.url,
            )
        return "-"

    preview_small.short_description = "Фото"


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("image_tag", "name", "get_services_count")
    list_display_links = ("name",)
    search_fields = ("name",)
    inlines = [ServiceInline]
    readonly_fields = ("preview_large",)

    fieldsets = (
        (
            "Визуализация",
            {
                "fields": ("image", "preview_large"),
            },
        ),
        ("Основное", {"fields": ("name", "desc")}),
    )

    def get_services_count(self, obj):
        return obj.services.count()

    get_services_count.short_description = "Кол-во услуг"

    def image_tag(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 90px; height: 45px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "—"

    image_tag.short_description = "Иконка"

    def preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; border-radius: 10px;" />',
                obj.image.url,
            )
        return "Картинка не загружена"

    preview_large.short_description = "Предпросмотр"


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("preview_image", "title", "game", "price", "author")
    list_display_links = ("title",)
    list_editable = ("price",)
    list_filter = ("game",)
    search_fields = ("title", "description")
    readonly_fields = ("preview_large",)

    fieldsets = (
        (
            "Визуализация",
            {
                "fields": ("image", "preview_large"),
            },
        ),
        ("Основное", {"fields": ("title", "game", "author", "price")}),
        ("Контент", {"fields": ("description",)}),
    )

    def preview_image(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="width: 50px; height: 35px; object-fit: cover; border-radius: 4px;" />',
                obj.image.url,
            )
        return "—"

    preview_image.short_description = "Превью"

    def preview_large(self, obj):
        if obj.image:
            return format_html(
                '<img src="{}" style="max-height: 200px; border-radius: 10px;" />',
                obj.image.url,
            )
        return "Картинка не загружена"

    preview_large.short_description = "Просмотр"

    def save_model(self, request, obj, form, change):
        if not obj.author_id:
            obj.author = request.user
        super().save_model(request, obj, form, change)
