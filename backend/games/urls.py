from django.urls import path
from .views import (
    service_catalog,
    add_to_cart,
    cart_detail,
    remove_from_cart,
    get_cart_count,
    service_create,
    service_delete,
    service_edit,
    service_detail,
    index,
    add_review,
    seller_profile,
)

urlpatterns = [
    path("", index, name="index"),
    path("catalog", service_catalog, name="catalog"),
    path("cart/", cart_detail, name="cart"),
    path("cart/add/<int:service_id>/", add_to_cart, name="add_to_cart"),
    path("cart/remove/<int:service_id>/", remove_from_cart, name="remove_from_cart"),
    path("cart-count/", get_cart_count, name="cart_count"),
    path("service/<int:pk>/", service_detail, name="service_detail"),
    path("service/add/", service_create, name="service_create"),
    path("service/<int:pk>/edit/", service_edit, name="service_edit"),
    path("service/<int:pk>/delete/", service_delete, name="service_delete"),
    path("service/<int:service_id>/review/", add_review, name="add_review"),
    path("seller/<str:email>/", seller_profile, name="seller_profile"),
]
