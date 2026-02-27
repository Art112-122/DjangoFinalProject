from django.contrib import admin
from django.utils.html import format_html
from .models import Game, Service, Review


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 0
    classes = ("collapse",)
    readonly_fields = ("preview_small",)
    fields = ("preview_small", "title", "price", "author", "get_avr_rating")

    def get_avg_rating(self, obj):
        from django.db.models import Avg

        avg = obj.reviews.aggregate(Avg("rating"))["rating__avg"]
        if avg:
            return format_html('<b style="color: #f39c12;">{:.1f} ★</b>', avg)
        return "Нет оценок"

    get_avg_rating.short_description = "Рейтинг"

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


class ReviewInline(admin.TabularInline):
    model = Review
    extra = 0
    readonly_fields = ("author", "created_at")
    classes = ("collapse",)


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ("service", "author", "rating_stars", "created_at")
    list_filter = ("rating", "created_at", "service__game")
    search_fields = ("text", "author__username", "service__title")

    def rating_stars(self, obj):
        return "★" * obj.rating + "☆" * (5 - obj.rating)

    rating_stars.short_description = "Рейтинг"

