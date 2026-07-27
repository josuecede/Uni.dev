from django.contrib import admin
from .models import Platform, Genre, Category, Product, ProductImage, SystemRequirement, Order, OrderItem

admin.site.register(Platform)
admin.site.register(Genre)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(ProductImage)
admin.site.register(SystemRequirement)
admin.site.register(Order)
admin.site.register(OrderItem)
