from django.contrib import admin
from .models import Product, Order, Wishlist

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['name', 'price']
    search_fields = ['name', 'description']
    list_filter = ['price']

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ['id', 'name', 'email', 'total_price', 'created_at', 'user']
    list_filter = ['created_at', 'user']
    search_fields = ['name', 'email']

@admin.register(Wishlist)
class WishlistAdmin(admin.ModelAdmin):
    list_display = ['user', 'created_at']
    filter_horizontal = ['products']
