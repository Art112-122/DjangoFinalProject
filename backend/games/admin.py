from django.contrib import admin
from .models import Game, Service


class ServiceInline(admin.TabularInline):
    model = Service
    extra = 1  


@admin.register(Game)
class GameAdmin(admin.ModelAdmin):
    list_display = ("name",) 
    inlines = [ServiceInline]  


@admin.register(Service)
class ServiceAdmin(admin.ModelAdmin):
    list_display = ("title", "game", "price")  
    list_filter = ("game",)  
    search_fields = ("title", "description") 
