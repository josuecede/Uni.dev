from django.contrib import admin
from .models import Cart, CartItem, Coupon, DigitalKey

admin.site.register(Cart)
admin.site.register(CartItem)
admin.site.register(Coupon)
admin.site.register(DigitalKey)
