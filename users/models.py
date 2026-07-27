from django.contrib.auth.models import AbstractUser
from django.db import models
from django.core.validators import FileExtensionValidator


class CustomUser(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = 'ADMIN', 'Administrador'
        MANAGER = 'MANAGER', 'Encargado de Tienda'
        CUSTOMER = 'CUSTOMER', 'Cliente'

    role = models.CharField('Rol', max_length=10, choices=Role.choices, default=Role.CUSTOMER)
    profile_picture = models.ImageField('Foto de perfil', upload_to='profile_pics/', default='profile_pics/default.png', validators=[FileExtensionValidator(['jpg', 'jpeg', 'png'])])
    phone_number = models.CharField('Teléfono', max_length=15, blank=True)
    bio = models.TextField('Biografía', blank=True)
    address = models.TextField('Dirección', blank=True)
    reset_code = models.CharField('Código de recuperación', max_length=6, null=True, blank=True)
    reset_code_expiry = models.DateTimeField('Expiración del código', null=True, blank=True)
    verification_code = models.CharField('Código de verificación', max_length=6, null=True, blank=True)
    verification_code_expiry = models.DateTimeField('Expiración del código de verificación', null=True, blank=True)
    theme = models.CharField('Tema', max_length=5, choices=[('dark', 'Oscuro'), ('light', 'Claro')], default='dark')

    class Meta:
        verbose_name = 'Usuario'
        verbose_name_plural = 'Usuarios'

    def is_admin(self):
        return self.role == self.Role.ADMIN

    def is_manager(self):
        return self.role == self.Role.MANAGER

    def is_customer(self):
        return self.role == self.Role.CUSTOMER
