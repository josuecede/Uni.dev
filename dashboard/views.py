from datetime import datetime, timedelta
from django.shortcuts import render, redirect, get_object_or_404
from django.db.models import Sum, Count, Q
from django.contrib import messages
from django.contrib.auth import update_session_auth_hash
from django.http import JsonResponse
from django.utils import timezone
from .decorators import staff_required, admin_required
from .models import Product, ProductImage, Category, Order, OrderItem
from store.models import Coupon
from .forms import ProductForm, CategoryForm, OrderStatusForm, AdminUserCreateForm, AdminUserEditForm, AdminPasswordForm
from users.models import CustomUser


@staff_required
def home(request):
    now = timezone.now()
    first_of_month = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
    first_of_year = now.replace(month=1, day=1, hour=0, minute=0, second=0, microsecond=0)

    month_orders = Order.objects.filter(created_at__gte=first_of_month)
    year_orders = Order.objects.filter(created_at__gte=first_of_year)

    total_revenue_month = month_orders.aggregate(s=Sum('total'))['s'] or 0
    total_revenue_year = year_orders.aggregate(s=Sum('total'))['s'] or 0
    orders_count = year_orders.count()
    avg_ticket = total_revenue_year / orders_count if orders_count else 0
    low_stock = Product.objects.filter(stock__lt=5, is_active=True).count()

    sales_by_category = (
        OrderItem.objects
        .filter(order__created_at__gte=first_of_year)
        .values('product__category__name')
        .annotate(total=Sum('price'))
        .order_by('-total')
    )

    sales_trend = (
        Order.objects
        .filter(created_at__gte=first_of_year)
        .extra(select={'month': "strftime('%%m', created_at)"})
        .values('month')
        .annotate(total=Sum('total'))
        .order_by('month')
    )

    def to_float(v):
        return float(v) if v is not None else 0

    sales_by_category_list = [{**r, 'total': to_float(r['total'])} for r in sales_by_category]
    sales_trend_list = [{**r, 'total': to_float(r['total'])} for r in sales_trend]

    return render(request, 'index.html', {
        'total_revenue_month': total_revenue_month,
        'total_revenue_year': total_revenue_year,
        'orders_count': orders_count,
        'avg_ticket': avg_ticket,
        'low_stock': low_stock,
        'sales_by_category': sales_by_category_list,
        'sales_trend': sales_trend_list,
    })


@staff_required
def product_list(request):
    products = Product.objects.all()
    if request.method == 'POST' and 'toggle_active' in request.POST:
        product = get_object_or_404(Product, id=request.POST['product_id'])
        product.is_active = not product.is_active
        product.save()
        messages.success(request, f'Producto {"activado" if product.is_active else "desactivado"}.')
        return redirect('dashboard:product_list')
    return render(request, 'pages/tables/data.html', {'products': products})


@staff_required
def product_create(request):
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto creado.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm()
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Nuevo Producto'})


@staff_required
def product_edit(request, pk):
    product = get_object_or_404(Product, id=pk)
    if request.method == 'POST':
        form = ProductForm(request.POST, request.FILES, instance=product)
        if form.is_valid():
            form.save()
            messages.success(request, 'Producto actualizado.')
            return redirect('dashboard:product_list')
    else:
        form = ProductForm(instance=product)
    return render(request, 'dashboard/product_form.html', {'form': form, 'title': 'Editar Producto', 'product': product})


@staff_required
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'pages/tables/simple.html', {'categories': categories})


@staff_required
def category_create(request):
    if request.method == 'POST':
        form = CategoryForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría creada.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm()
    return render(request, 'pages/forms/general.html', {'form': form, 'title': 'Nueva Categoría'})


@staff_required
def category_edit(request, pk):
    category = get_object_or_404(Category, id=pk)
    if request.method == 'POST':
        form = CategoryForm(request.POST, instance=category)
        if form.is_valid():
            form.save()
            messages.success(request, 'Categoría actualizada.')
            return redirect('dashboard:category_list')
    else:
        form = CategoryForm(instance=category)
    return render(request, 'pages/forms/general.html', {'form': form, 'title': 'Editar Categoría'})


@staff_required
def category_delete(request, pk):
    category = get_object_or_404(Category, id=pk)
    if request.method == 'POST':
        category.delete()
        messages.success(request, f'Categoría "{category.name}" eliminada.')
    return redirect('dashboard:category_list')


@admin_required
def order_list(request):
    orders = Order.objects.all()
    status = request.GET.get('status')
    if status:
        orders = orders.filter(status=status)
    return render(request, 'pages/tables/order_list.html', {'orders': orders})


@admin_required
def order_detail(request, pk):
    order = get_object_or_404(Order, id=pk)
    if request.method == 'POST':
        form = OrderStatusForm(request.POST, instance=order)
        if form.is_valid():
            form.save()
            messages.success(request, 'Estado actualizado.')
            return redirect('dashboard:order_detail', pk=order.id)
    else:
        form = OrderStatusForm(instance=order)
    return render(request, 'pages/examples/invoice.html', {'order': order, 'form': form})


@admin_required
def user_list(request):
    users = CustomUser.objects.all()
    return render(request, 'pages/tables/user_list.html', {'users': users})


@admin_required
def user_create(request):
    if request.method == 'POST':
        form = AdminUserCreateForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario creado.')
            return redirect('dashboard:user_list')
    else:
        form = AdminUserCreateForm()
    return render(request, 'pages/forms/general.html', {'form': form, 'title': 'Nuevo Usuario'})


@admin_required
def user_edit(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    if request.method == 'POST':
        form = AdminUserEditForm(request.POST, instance=user)
        if form.is_valid():
            form.save()
            messages.success(request, 'Usuario actualizado.')
            return redirect('dashboard:user_list')
    else:
        form = AdminUserEditForm(instance=user)
    return render(request, 'pages/forms/general.html', {'form': form, 'title': f'Editar Usuario: {user.username}'})


@admin_required
def user_change_password(request, pk):
    user = get_object_or_404(CustomUser, id=pk)
    if request.method == 'POST':
        form = AdminPasswordForm(request.POST)
        if form.is_valid():
            user.set_password(form.cleaned_data['password'])
            user.save()
            messages.success(request, f'Contraseña de {user.username} cambiada.')
            return redirect('dashboard:user_list')
    else:
        form = AdminPasswordForm()
    return render(request, 'pages/forms/password_form.html', {'form': form, 'title': f'Cambiar Contraseña: {user.username}', 'target_user': user})



@admin_required
def coupon_list(request):
    coupons = Coupon.objects.all().order_by('-valid_until')
    return render(request, 'dashboard/coupon_list.html', {'coupons': coupons})


@admin_required
def coupon_create(request):
    if request.method == 'POST':
        code = request.POST.get('code', '').upper()
        discount_percent = request.POST.get('discount_percent')
        valid_until = request.POST.get('valid_until')
        max_uses = request.POST.get('max_uses', 1)
        if code and discount_percent and valid_until:
            Coupon.objects.create(
                code=code,
                discount_percent=int(discount_percent),
                valid_until=valid_until,
                max_uses=int(max_uses),
            )
            messages.success(request, 'Cupón creado.')
            return redirect('dashboard:coupon_list')
        messages.error(request, 'Completa todos los campos.')
    return render(request, 'dashboard/coupon_form.html', {'title': 'Nuevo Cupón'})


@admin_required
def coupon_edit(request, pk):
    coupon = get_object_or_404(Coupon, id=pk)
    if request.method == 'POST':
        coupon.code = request.POST.get('code', coupon.code).upper()
        coupon.discount_percent = int(request.POST.get('discount_percent', coupon.discount_percent))
        coupon.valid_until = request.POST.get('valid_until', coupon.valid_until)
        coupon.max_uses = int(request.POST.get('max_uses', coupon.max_uses))
        coupon.save()
        messages.success(request, 'Cupón actualizado.')
        return redirect('dashboard:coupon_list')
    return render(request, 'dashboard/coupon_form.html', {'coupon': coupon, 'title': 'Editar Cupón'})


@staff_required
def product_add_image(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=request.POST.get('product_id'))
        for f in request.FILES.getlist('images'):
            ProductImage.objects.create(product=product, image=f)
        messages.success(request, 'Imágenes agregadas.')
        return redirect(request.META.get('HTTP_REFERER', 'dashboard:product_list'))
    return redirect('dashboard:product_list')


@staff_required
def product_delete_image(request):
    if request.method == 'POST':
        img = get_object_or_404(ProductImage, id=request.POST.get('image_id'))
        img.delete()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)


@staff_required
def product_set_primary(request):
    if request.method == 'POST':
        product = get_object_or_404(Product, id=request.POST.get('product_id'))
        img = get_object_or_404(ProductImage, id=request.POST.get('image_id'), product=product)
        ProductImage.objects.filter(product=product, is_primary=True).update(is_primary=False)
        img.is_primary = True
        img.save()
        return JsonResponse({'success': True})
    return JsonResponse({'success': False}, status=400)
