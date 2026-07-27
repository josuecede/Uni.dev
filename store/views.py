import json
import random
import string
from django.shortcuts import render, redirect, get_object_or_404
from django.http import JsonResponse, HttpResponse
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.core.mail import send_mail
from django.template.loader import render_to_string
from django.utils import timezone
from django.core.paginator import Paginator
from django.db.models import Q, Min, Max, F, Value, ExpressionWrapper, FloatField
from django.db.models.functions import Coalesce
from dashboard.models import Product, Platform, Genre, Category, Order, OrderItem
from users.forms import CustomUserCreationForm
from users.models import CustomUser
from .models import Cart, CartItem, Coupon, DigitalKey, Wishlist


def catalog(request):
    final_price_expr = ExpressionWrapper(
        F('price') * (Value(100) - Coalesce(F('discount_percent'), Value(0))) / Value(100),
        output_field=FloatField()
    )

    products = Product.objects.filter(is_active=True).annotate(discounted_price=final_price_expr)
    platforms = Platform.objects.all()
    genres = Genre.objects.all()
    categories = Category.objects.all()

    platform = request.GET.get('platform')
    genre = request.GET.get('genre')
    category = request.GET.get('category')
    format = request.GET.get('format')
    sort = request.GET.get('sort', 'name')
    q = request.GET.get('q', '')
    min_price = request.GET.get('min_price')
    max_price = request.GET.get('max_price')

    if q:
        products = products.filter(name__icontains=q)
    if platform:
        products = products.filter(platforms__slug=platform)
    if genre:
        products = products.filter(genres__slug=genre)
    if category:
        products = products.filter(category_id=category)
    if format:
        products = products.filter(format=format)

    price_range = products.aggregate(min=Min('price'), max=Max('price'))

    if min_price:
        products = products.filter(discounted_price__gte=float(min_price))
    if max_price:
        products = products.filter(discounted_price__lte=float(max_price))

    sort_map = {
        'price_asc': 'discounted_price',
        'price_desc': '-discounted_price',
        'newest': '-created_at',
        'name': 'name',
        'rating': '-rating',
    }
    products = products.order_by(sort_map.get(sort, 'name'))

    paginator = Paginator(products, 12)
    page = request.GET.get('page', 1)
    products_page = paginator.get_page(page)

    wishlist_ids = []
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.count
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_ids = list(wishlist.products.values_list('id', flat=True))

    return render(request, 'store/catalog.html', {
        'products': products_page,
        'platforms': platforms,
        'genres': genres,
        'categories': categories,
        'price_range': price_range,
        'cart_count': cart_count,
        'wishlist_ids': wishlist_ids,
    })


def product_detail(request, pk):
    product = get_object_or_404(Product.objects.filter(is_active=True), id=pk)
    related = Product.objects.filter(
        Q(platforms__in=product.platforms.all()) | Q(genres__in=product.genres.all()),
        is_active=True
    ).exclude(id=product.id).distinct()[:8]

    wishlist_ids = []
    cart_count = 0
    if request.user.is_authenticated:
        cart = Cart.objects.filter(user=request.user).first()
        if cart:
            cart_count = cart.count
        wishlist = Wishlist.objects.filter(user=request.user).first()
        if wishlist:
            wishlist_ids = list(wishlist.products.values_list('id', flat=True))

    return render(request, 'store/product_detail.html', {
        'product': product,
        'related': related,
        'cart_count': cart_count,
        'wishlist_ids': wishlist_ids,
    })


def add_to_cart(request):
    if not request.user.is_authenticated:
        return JsonResponse({'success': False, 'redirect': '/store/register/'}, status=401)
    if request.method == 'POST':
        data = json.loads(request.body)
        product_id = data.get('product_id')
        quantity = int(data.get('quantity', 1))
        product = get_object_or_404(Product, id=product_id, is_active=True)

        cart, _ = Cart.objects.get_or_create(user=request.user)
        item, created = CartItem.objects.get_or_create(cart=cart, product=product)
        if not created:
            item.quantity += quantity
        item.save()

        return JsonResponse({'success': True, 'count': cart.count, 'total': str(cart.total)})
    return JsonResponse({'success': False}, status=400)


@login_required
def cart_data(request):
    cart = Cart.objects.filter(user=request.user).first()
    items = []
    total = 0
    count = 0
    if cart:
        for item in cart.items.all():
            items.append({
                'id': item.id,
                'product_id': item.product.id,
                'name': item.product.name,
                'image': item.product.image.url if item.product.image else '',
                'price': str(item.product.final_price),
                'quantity': item.quantity,
                'subtotal': str(item.subtotal),
                'platforms': [{'name': p.name, 'color': p.color} for p in item.product.platforms.all()],
            })
        total = str(cart.total)
        count = cart.count
    return JsonResponse({'items': items, 'total': total, 'count': count})


@login_required
def update_cart_item(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        item = get_object_or_404(CartItem, id=data['item_id'], cart__user=request.user)
        action = data.get('action')
        if action == 'increase':
            item.quantity += 1
            item.save()
        elif action == 'decrease':
            item.quantity -= 1
            if item.quantity <= 0:
                item.delete()
                return JsonResponse({'success': True, 'deleted': True, 'count': Cart.objects.get(user=request.user).count})
            item.save()
        elif action == 'remove':
            item.delete()
            return JsonResponse({'success': True, 'deleted': True, 'count': Cart.objects.get(user=request.user).count})

        cart = Cart.objects.get(user=request.user)
        return JsonResponse({
            'success': True,
            'subtotal': str(item.subtotal),
            'total': str(cart.total),
            'count': cart.count,
        })
    return JsonResponse({'success': False}, status=400)


@login_required
def checkout(request):
    cart = Cart.objects.filter(user=request.user).first()
    if not cart or cart.count == 0:
        messages.warning(request, 'Tu carrito está vacío.')
        return redirect('store:catalog')

    if request.method == 'POST':
        shipping_address = request.POST.get('shipping_address', '')
        coupon_code = request.POST.get('coupon_code', '')

        discount = 0
        if coupon_code:
            coupon = Coupon.objects.filter(code=coupon_code.upper()).first()
            if coupon and coupon.is_valid:
                discount = coupon.discount_percent
                coupon.used_count += 1
                coupon.save()
            else:
                messages.warning(request, 'Cupón inválido o expirado.')

        total = cart.total * (100 - discount) / 100 if discount else cart.total

        order = Order.objects.create(
            customer=request.user,
            total=total,
            shipping_address=shipping_address or 'Entrega digital',
        )

        all_digital = True
        for cart_item in cart.items.all():
            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                quantity=cart_item.quantity,
                price=cart_item.product.final_price,
            )

            if cart_item.product.format == 'DIGITAL':
                keys_qty = cart_item.quantity
                for key in DigitalKey.objects.filter(product=cart_item.product, is_sold=False)[:keys_qty]:
                    key.is_sold = True
                    key.order_item = OrderItem.objects.filter(order=order, product=cart_item.product).first()
                    key.save()
            else:
                all_digital = False

        if all_digital:
            order.status = 'DELIVERED'
            order.save()

        cart.delete()
        return redirect('store:checkout_confirm', order_id=order.id)

    return render(request, 'store/checkout.html', {
        'cart': cart,
        'cart_count': cart.count,
    })


@login_required
def checkout_confirm(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    keys = DigitalKey.objects.filter(order_item__order=order)
    return render(request, 'store/checkout_confirm.html', {
        'order': order,
        'keys': keys,
        'cart_count': 0,
    })


@login_required
def order_history(request):
    orders = Order.objects.filter(customer=request.user).order_by('-created_at')
    cart_count = 0
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_count = cart.count
    return render(request, 'store/order_history.html', {
        'orders': orders,
        'cart_count': cart_count,
    })


@login_required
def order_detail(request, order_id):
    order = get_object_or_404(Order, id=order_id, customer=request.user)
    keys = DigitalKey.objects.filter(order_item__order=order)
    cart_count = 0
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_count = cart.count
    return render(request, 'store/order_detail.html', {
        'order': order,
        'keys': keys,
        'cart_count': cart_count,
    })


@login_required
def wishlist_list(request):
    wishlist = Wishlist.objects.filter(user=request.user).first()
    products = wishlist.products.all() if wishlist else []
    cart_count = 0
    cart = Cart.objects.filter(user=request.user).first()
    if cart:
        cart_count = cart.count
    return render(request, 'store/wishlist.html', {
        'products': products,
        'cart_count': cart_count,
    })


@login_required
def wishlist_toggle(request):
    if request.method == 'POST':
        data = json.loads(request.body)
        product = get_object_or_404(Product, id=data.get('product_id'))
        wishlist, _ = Wishlist.objects.get_or_create(user=request.user)
        if wishlist.products.filter(id=product.id).exists():
            wishlist.products.remove(product)
            return JsonResponse({'in_wishlist': False})
        else:
            wishlist.products.add(product)
            return JsonResponse({'in_wishlist': True})
    return JsonResponse({'success': False}, status=400)


@login_required
def rate_product(request, pk):
    if request.method == 'POST':
        data = json.loads(request.body)
        rating = float(data.get('rating', 0))
        product = get_object_or_404(Product, id=pk, is_active=True)
        product.rating = min(5, max(0, rating))
        product.save()
        return JsonResponse({'success': True, 'rating': product.rating})
    return JsonResponse({'success': False}, status=400)


def quick_view(request, pk):
    product = get_object_or_404(Product.objects.filter(is_active=True), id=pk)
    return render(request, 'store/quick_view.html', {'product': product})


@login_required
def library(request):
    items = OrderItem.objects.filter(order__customer=request.user).select_related('product', 'order').order_by('-order__created_at')
    keys_qs = DigitalKey.objects.filter(is_sold=True, order_item__order__customer=request.user)
    key_map = {k.order_item_id: k.key for k in keys_qs}
    library_items = []
    for item in items:
        library_items.append({
            'item': item,
            'key': key_map.get(item.id),
        })
    return render(request, 'store/library.html', {
        'library_items': library_items,
    })


def login_view(request):
    if request.method == 'POST':
        username = request.POST['username']
        password = request.POST['password']
        user = authenticate(request, username=username, password=password)
        if user:
            login(request, user)
            messages.success(request, f'Bienvenido {user.username}.')
            return redirect(request.GET.get('next', 'store:catalog'))
        messages.error(request, 'Usuario o contraseña incorrectos.')
    return render(request, 'store/login.html')


def register_view(request):
    if request.method == 'POST':
        email = request.POST.get('email', '').strip().lower()
        existing = CustomUser.objects.filter(email__iexact=email).first()
        if existing and not existing.is_active:
            code = f'{random.randint(100000, 999999)}'
            existing.verification_code = code
            existing.verification_code_expiry = timezone.now() + timezone.timedelta(minutes=15)
            existing.save()
            subject = 'Verifica tu correo - GameStore'
            html_message = render_to_string('registration/verify_email.html', {'code': code})
            send_mail(subject, '', None, [existing.email], html_message=html_message, fail_silently=False)
            messages.success(request, 'Te reenviamos el código de verificación a tu correo.')
            request.session['verify_email'] = existing.email
            return redirect('store:register_verify')
        form = CustomUserCreationForm(request.POST, request.FILES)
        if form.is_valid():
            user = form.save(commit=False)
            user.email = user.email.lower()
            user.is_active = False
            code = f'{random.randint(100000, 999999)}'
            user.verification_code = code
            user.verification_code_expiry = timezone.now() + timezone.timedelta(minutes=15)
            user.save()
            subject = 'Verifica tu correo - GameStore'
            html_message = render_to_string('registration/verify_email.html', {'code': code})
            send_mail(subject, '', None, [user.email], html_message=html_message, fail_silently=False)
            messages.success(request, 'Te enviamos un código de verificación a tu correo.')
            request.session['verify_email'] = user.email
            return redirect('store:register_verify')
    else:
        form = CustomUserCreationForm()
    return render(request, 'store/register.html', {'form': form})


def register_verify_view(request):
    email = request.session.get('verify_email', '')
    if request.method == 'POST':
        email = request.POST.get('email', email).strip().lower()
        code = request.POST.get('code', '').strip()
        user = CustomUser.objects.filter(email__iexact=email, verification_code=code, verification_code_expiry__gte=timezone.now()).first()
        if user:
            user.is_active = True
            user.verification_code = None
            user.verification_code_expiry = None
            user.save()
            login(request, user)
            messages.success(request, 'Registro exitoso.')
            return redirect('store:catalog')
        messages.error(request, 'Código inválido o expirado.')
    return render(request, 'store/register_verify.html', {'email': email})


def register_resend_code(request):
    email = request.session.get('verify_email', '')
    if not email:
        messages.error(request, 'Sesión expirada. Regístrate nuevamente.')
        return redirect('store:register')
    user = CustomUser.objects.filter(email__iexact=email, is_active=False).first()
    if not user:
        messages.error(request, 'Cuenta no encontrada o ya verificada.')
        return redirect('store:register')
    code = f'{random.randint(100000, 999999)}'
    user.verification_code = code
    user.verification_code_expiry = timezone.now() + timezone.timedelta(minutes=15)
    user.save()
    subject = 'Verifica tu correo - GameStore'
    html_message = render_to_string('registration/verify_email.html', {'code': code})
    send_mail(subject, '', None, [user.email], html_message=html_message, fail_silently=False)
    messages.success(request, 'Código reenviado a tu correo.')
    return redirect('store:register_verify')
