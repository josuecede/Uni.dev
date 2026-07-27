from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordChangeForm
from .models import Product, Platform, Category, Order
from users.models import CustomUser


class ProductForm(forms.ModelForm):
    class Meta:
        model = Product
        fields = ('name', 'description', 'price', 'discount_percent', 'stock', 'format', 'platforms', 'category', 'image', 'developer', 'publisher', 'release_date', 'rating', 'video_url', 'is_featured', 'is_new_release', 'is_active')
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
            'price': 'Precio',
            'discount_percent': 'Descuento %',
            'stock': 'Stock',
            'format': 'Formato',
            'platforms': 'Plataformas',
            'category': 'Categoría',
            'image': 'Portada',
            'developer': 'Desarrollador',
            'publisher': 'Editor',
            'release_date': 'Fecha de lanzamiento',
            'rating': 'Valoración',
            'video_url': 'URL de video (tráiler)',
            'is_featured': 'Destacado',
            'is_new_release': 'Nuevo lanzamiento',
            'is_active': 'Activo',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del juego'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Descripción del juego'}),
            'price': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.01'}),
            'discount_percent': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
            'stock': forms.NumberInput(attrs={'class': 'form-control', 'min': '0'}),
            'format': forms.Select(attrs={'class': 'form-control'}),
            'platforms': forms.SelectMultiple(attrs={'class': 'form-control', 'size': '5'}),
            'category': forms.Select(attrs={'class': 'form-control'}),
            'image': forms.FileInput(attrs={'class': 'form-control-file'}),
            'developer': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Desarrollador'}),
            'publisher': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Editor'}),
            'release_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'rating': forms.NumberInput(attrs={'class': 'form-control', 'step': '0.1', 'min': '0', 'max': '10'}),
            'video_url': forms.URLInput(attrs={'class': 'form-control', 'placeholder': 'https://www.youtube.com/...'}),
            'is_featured': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_new_release': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class PlatformForm(forms.ModelForm):
    class Meta:
        model = Platform
        fields = ('name', 'slug', 'icon', 'color')
        labels = {
            'name': 'Nombre',
            'slug': 'Slug (URL)',
            'icon': 'Icono (clase Bootstrap)',
            'color': 'Color (hex)',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: PlayStation 5'}),
            'slug': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: ps5'}),
            'icon': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Ej: bi-playstation'}),
            'color': forms.TextInput(attrs={'class': 'form-control', 'type': 'color'}),
        }


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ('name', 'description')
        labels = {
            'name': 'Nombre',
            'description': 'Descripción',
        }
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre de la categoría'}),
            'description': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Descripción (opcional)'}),
        }


class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ('status',)
        labels = {
            'status': 'Estado',
        }


class AdminUserCreateForm(UserCreationForm):
    role = forms.ChoiceField(label='Rol', choices=CustomUser.Role.choices, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta(UserCreationForm.Meta):
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'role')
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
        }
        help_texts = {'username': None}
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
        }


class AdminUserEditForm(forms.ModelForm):
    role = forms.ChoiceField(label='Rol', choices=CustomUser.Role.choices, widget=forms.Select(attrs={'class': 'form-control'}))

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'first_name', 'last_name', 'phone_number', 'bio', 'address', 'role', 'is_active')
        labels = {
            'username': 'Nombre de usuario',
            'email': 'Correo electrónico',
            'first_name': 'Nombre',
            'last_name': 'Apellidos',
            'phone_number': 'Teléfono',
            'bio': 'Biografía',
            'address': 'Dirección',
            'is_active': 'Activo',
        }
        widgets = {
            'username': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
            'first_name': forms.TextInput(attrs={'class': 'form-control'}),
            'last_name': forms.TextInput(attrs={'class': 'form-control'}),
            'phone_number': forms.TextInput(attrs={'class': 'form-control'}),
            'bio': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'address': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
        }


class AdminPasswordForm(forms.Form):
    password = forms.CharField(label='Nueva contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    password_confirm = forms.CharField(label='Confirmar contraseña', widget=forms.PasswordInput(attrs={'class': 'form-control'}))

    def clean(self):
        cleaned_data = super().clean()
        p1 = cleaned_data.get('password')
        p2 = cleaned_data.get('password_confirm')
        if p1 and p2 and p1 != p2:
            raise forms.ValidationError('Las contraseñas no coinciden.')
        return cleaned_data
