from django.db import models
from django.conf import settings
from dashboard.models import Product


class Cart(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Carrito'
        verbose_name_plural = 'Carritos'

    @property
    def total(self):
        return sum(item.subtotal for item in self.items.all())

    @property
    def count(self):
        return sum(item.quantity for item in self.items.all())

    def __str__(self):
        return f'Carrito de {self.user.username}'


class CartItem(models.Model):
    cart = models.ForeignKey(Cart, related_name='items', on_delete=models.CASCADE, verbose_name='Carrito')
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    quantity = models.PositiveIntegerField('Cantidad', default=1)

    class Meta:
        verbose_name = 'Ítem del carrito'
        verbose_name_plural = 'Ítems del carrito'

    @property
    def subtotal(self):
        return self.product.final_price * self.quantity

    def __str__(self):
        return f'{self.quantity}x {self.product.name}'


class Coupon(models.Model):
    code = models.CharField('Código', max_length=20, unique=True)
    discount_percent = models.PositiveIntegerField('Descuento %')
    valid_until = models.DateTimeField('Válido hasta')
    max_uses = models.PositiveIntegerField('Usos máximos', default=1)
    used_count = models.PositiveIntegerField('Usos actuales', default=0)

    class Meta:
        verbose_name = 'Cupón'
        verbose_name_plural = 'Cupones'

    @property
    def is_valid(self):
        from django.utils import timezone
        return self.used_count < self.max_uses and self.valid_until > timezone.now()

    def __str__(self):
        return self.code


class Wishlist(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario')
    products = models.ManyToManyField(Product, verbose_name='Productos')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Lista de deseos'
        verbose_name_plural = 'Listas de deseos'

    def __str__(self):
        return f'Wishlist de {self.user.username}'


class DigitalKey(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, verbose_name='Producto')
    key = models.CharField('Clave', max_length=100, unique=True)
    is_sold = models.BooleanField('Vendida', default=False)
    order_item = models.ForeignKey('dashboard.OrderItem', on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Ítem de orden')

    class Meta:
        verbose_name = 'Clave digital'
        verbose_name_plural = 'Claves digitales'

    def __str__(self):
        return f'{self.product.name} - {self.key[:20]}...'
