from django.urls import path
from .views import product_list, cart_view, add_to_cart, remove_from_cart, checkout, thank_you, wishlist_view, add_to_wishlist, remove_from_wishlist, clear_cart, product_detail

urlpatterns = [
    path('', product_list, name='product_list'),
    path('cart/', cart_view, name='cart_view'),
    path('add-to-cart/<int:product_id>/', add_to_cart, name='add_to_cart'),
    path('remove-from-cart/<int:product_id>/', remove_from_cart, name='remove_from_cart'),
    path('checkout/', checkout, name='checkout'),
    path('thank-you/<int:order_id>/', thank_you, name='thank_you'),
    path('wishlist/', wishlist_view, name='wishlist_view'),
    path('add-to-wishlist/<int:product_id>/', add_to_wishlist, name='add_to_wishlist'),
    path('remove-from-wishlist/<int:product_id>/', remove_from_wishlist, name='remove_from_wishlist'),
    path('clear-cart/', clear_cart, name='clear_cart'),
    path('product/<int:product_id>/', product_detail, name='product_detail'),
] 