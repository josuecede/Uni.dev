from django.urls import path
from . import views

app_name = 'dashboard'

urlpatterns = [
    path('', views.home, name='home'),
    path('productos/', views.product_list, name='product_list'),
    path('productos/nuevo/', views.product_create, name='product_create'),
    path('productos/<int:pk>/editar/', views.product_edit, name='product_edit'),
    path('categorias/', views.category_list, name='category_list'),
    path('categorias/nueva/', views.category_create, name='category_create'),
    path('categorias/<int:pk>/editar/', views.category_edit, name='category_edit'),
    path('categorias/<int:pk>/eliminar/', views.category_delete, name='category_delete'),
    path('productos/agregar-imagen/', views.product_add_image, name='product_add_image'),
    path('productos/eliminar-imagen/', views.product_delete_image, name='product_delete_image'),
    path('productos/imagen-principal/', views.product_set_primary, name='product_set_primary'),
    path('pedidos/', views.order_list, name='order_list'),
    path('pedidos/<int:pk>/', views.order_detail, name='order_detail'),
    path('usuarios/', views.user_list, name='user_list'),
    path('usuarios/nuevo/', views.user_create, name='user_create'),
    path('usuarios/<int:pk>/editar/', views.user_edit, name='user_edit'),
    path('usuarios/<int:pk>/cambiar-password/', views.user_change_password, name='user_change_password'),
    path('cupones/', views.coupon_list, name='coupon_list'),
    path('cupones/nuevo/', views.coupon_create, name='coupon_create'),
    path('cupones/<int:pk>/editar/', views.coupon_edit, name='coupon_edit'),
]
