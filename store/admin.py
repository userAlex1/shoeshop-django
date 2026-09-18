from django.contrib import admin
from .models import Category, Product, Order, OrderItem


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'category', 'brand', 'price', 'stock', 'is_active')
    list_filter = ('category', 'brand', 'is_active')
    prepopulated_fields = {'slug': ('name',)}
    search_fields = ('name', 'brand')


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ('product', 'product_name', 'size', 'quantity', 'price')


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = ('order_number', 'full_name', 'phone', 'payment_method', 'status', 'total_amount', 'created_at')
    list_filter = ('status', 'payment_method')
    search_fields = ('order_number', 'full_name', 'phone', 'email')
    inlines = [OrderItemInline]
    readonly_fields = ('order_number', 'created_at', 'updated_at')
