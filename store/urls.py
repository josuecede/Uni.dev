from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('', views.catalog, name='catalog'),
    path('game/<int:pk>/', views.product_detail, name='product_detail'),
    path('product/quick/<int:pk>/', views.quick_view, name='quick_view'),
    path('product/<int:pk>/rate/', views.rate_product, name='rate_product'),
    path('cart/add/', views.add_to_cart, name='add_to_cart'),
    path('cart/data/', views.cart_data, name='cart_data'),
    path('cart/update/', views.update_cart_item, name='update_cart_item'),
    path('checkout/', views.checkout, name='checkout'),
    path('checkout/confirm/<int:order_id>/', views.checkout_confirm, name='checkout_confirm'),
    path('orders/', views.order_history, name='order_history'),
    path('orders/<int:order_id>/', views.order_detail, name='order_detail'),
    path('library/', views.library, name='library'),
    path('wishlist/', views.wishlist_list, name='wishlist'),
    path('wishlist/toggle/', views.wishlist_toggle, name='wishlist_toggle'),
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('register/verify/', views.register_verify_view, name='register_verify'),
    path('register/resend/', views.register_resend_code, name='register_resend'),
]
