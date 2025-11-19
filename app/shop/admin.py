from django.contrib import admin
from .models import Item, Order, Discount, Tax

@admin.register(Item)
class ItemAdmin(admin.ModelAdmin):
    """Настройка отображения товаров в админке."""
    list_display = ('name', 'price', 'currency')

class OrderItemInline(admin.TabularInline):
    """Позволяет добавлять товары прямо внутри страницы редактирования заказа."""
    model = Order.items.through
    extra = 1

@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    """Настройка отображения заказов."""
    list_display = ('pk', 'get_total_price')
    inlines = [OrderItemInline]
    exclude = ('items',)

admin.site.register(Discount)
admin.site.register(Tax)