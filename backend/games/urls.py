from django.urls import path
from .views import game_catalog, add_to_cart, cart_view, cart_count, remove_from_cart

urlpatterns = [
    path("", game_catalog, name="catalog"),
    path("cart/", cart_view, name="cart"),
    path("add/<int:game_id>/", add_to_cart, name="add_to_cart"),
    path("remove/<int:game_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart-count/", cart_count, name="cart_count"),
]
