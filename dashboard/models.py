from django.db import models
from django.conf import settings
from django.core.validators import FileExtensionValidator


class Platform(models.Model):
    name = models.CharField('Nombre', max_length=50, unique=True)
    slug = models.SlugField(unique=True)
    icon = models.CharField('Icono', max_length=50, help_text='Clase de Bootstrap Icons (ej: bi-pc-display)')
    color = models.CharField('Color', max_length=7, help_text='Ej: #003791 para PS5')

    class Meta:
        verbose_name = 'Plataforma'
        verbose_name_plural = 'Plataformas'

    def __str__(self):
        return self.name


class Genre(models.Model):
    name = models.CharField('Nombre', max_length=50, unique=True)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name = 'Género'
        verbose_name_plural = 'Géneros'

    def __str__(self):
        return self.name


class Category(models.Model):
    name = models.CharField('Nombre', max_length=100, unique=True)
    description = models.TextField('Descripción', blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Categoría'
        verbose_name_plural = 'Categorías'

    def __str__(self):
        return self.name


class Product(models.Model):
    class Format(models.TextChoices):
        DIGITAL = 'DIGITAL', 'Clave Digital'
        PHYSICAL = 'PHYSICAL', 'Físico'

    name = models.CharField('Nombre', max_length=200)
    description = models.TextField('Descripción')
    price = models.DecimalField('Precio', max_digits=10, decimal_places=2)
    discount_percent = models.PositiveIntegerField('Descuento %', default=0)
    stock = models.PositiveIntegerField('Stock', default=0)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, blank=True, verbose_name='Categoría')
    platforms = models.ManyToManyField(Platform, verbose_name='Plataformas')
    genres = models.ManyToManyField(Genre, verbose_name='Géneros')
    format = models.CharField('Formato', max_length=10, choices=Format.choices, default=Format.DIGITAL)
    image = models.ImageField('Portada', upload_to='products/', blank=True, validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    developer = models.CharField('Desarrollador', max_length=200, blank=True)
    publisher = models.CharField('Editor', max_length=200, blank=True)
    release_date = models.DateField('Fecha de lanzamiento', null=True, blank=True)
    rating = models.DecimalField('Valoración', max_digits=2, decimal_places=1, default=0)
    video_url = models.URLField('URL de video (tráiler)', blank=True)
    is_active = models.BooleanField('Activo', default=True)
    is_featured = models.BooleanField('Destacado', default=False)
    is_new_release = models.BooleanField('Nuevo lanzamiento', default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Producto'
        verbose_name_plural = 'Productos'

    @property
    def final_price(self):
        if self.discount_percent:
            return self.price * (100 - self.discount_percent) / 100
        return self.price

    @property
    def has_discount(self):
        return self.discount_percent > 0

    def __str__(self):
        return self.name


class ProductImage(models.Model):
    product = models.ForeignKey(Product, related_name='images', on_delete=models.CASCADE, verbose_name='Producto')
    image = models.ImageField('Imagen', upload_to='products/gallery/', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    is_primary = models.BooleanField('Principal', default=False)

    class Meta:
        verbose_name = 'Imagen del producto'
        verbose_name_plural = 'Imágenes del producto'

    def __str__(self):
        return f'Imagen de {self.product.name}'


class SystemRequirement(models.Model):
    class Type(models.TextChoices):
        MINIMUM = 'MINIMUM', 'Mínimos'
        RECOMMENDED = 'RECOMMENDED', 'Recomendados'

    product = models.ForeignKey(Product, related_name='requirements', on_delete=models.CASCADE, verbose_name='Producto')
    type = models.CharField('Tipo', max_length=11, choices=Type.choices)
    os = models.CharField('Sistema operativo', max_length=100)
    cpu = models.CharField('Procesador', max_length=200)
    ram = models.CharField('Memoria RAM', max_length=50)
    gpu = models.CharField('Tarjeta gráfica', max_length=200)
    storage = models.CharField('Almacenamiento', max_length=50)

    class Meta:
        verbose_name = 'Requisito del sistema'
        verbose_name_plural = 'Requisitos del sistema'

    def __str__(self):
        return f'Requisitos {self.get_type_display()} - {self.product.name}'


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING = 'PENDING', 'Pendiente'
        SHIPPED = 'SHIPPED', 'En Camino'
        DELIVERED = 'DELIVERED', 'Entregado'
        CANCELLED = 'CANCELLED', 'Cancelado'

    customer = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Cliente')
    status = models.CharField('Estado', max_length=10, choices=Status.choices, default=Status.PENDING)
    total = models.DecimalField('Total', max_digits=10, decimal_places=2, default=0)
    shipping_address = models.TextField('Dirección de envío')
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = 'Pedido'
        verbose_name_plural = 'Pedidos'

    def __str__(self):
        return f'Pedido #{self.id} - {self.customer.username}'


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE, verbose_name='Pedido')
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True, verbose_name='Producto')
    quantity = models.PositiveIntegerField('Cantidad', default=1)
    price = models.DecimalField('Precio', max_digits=10, decimal_places=2)

    class Meta:
        verbose_name = 'Detalle del pedido'
        verbose_name_plural = 'Detalles del pedido'

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f'{self.quantity}x {self.product.name if self.product else "N/A"}'


class HeroSection(models.Model):
    image = models.ImageField('Imagen de fondo', upload_to='hero/', blank=True, help_text='Imagen de fondo para el hero del inicio (1920x1080 recomendado)')
    is_active = models.BooleanField('Activo', default=False)

    class Meta:
        verbose_name = 'Hero de inicio'
        verbose_name_plural = 'Hero de inicio'

    def __str__(self):
        return f'Hero {"(activo)" if self.is_active else "(inactivo)"} - {self.image.name if self.image else "Sin imagen"}'


class OfferBanner(models.Model):
    message = models.TextField('Mensaje')
    is_active = models.BooleanField('Activo', default=False)
    link = models.URLField('Enlace (opcional)', blank=True)
    bg_color = models.CharField('Color de fondo', max_length=7, blank=True, help_text='Ej: #ff0000')
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = 'Barra de oferta'
        verbose_name_plural = 'Barras de ofertas'

    def __str__(self):
        return self.message[:50]
