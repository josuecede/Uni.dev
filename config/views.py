from django.shortcuts import render
from dashboard.models import Product, Platform, HeroSection
from store.models import Wishlist


def home(request):
    hero = HeroSection.objects.filter(is_active=True).first()
    platforms = Platform.objects.all()
    on_sale = Product.objects.filter(discount_percent__gt=0, is_active=True)[:6]
    new_releases = Product.objects.filter(is_new_release=True, is_active=True)[:8]
    latest_games = Product.objects.filter(is_active=True).order_by('-created_at')[:10]
    wishlist_ids = []
    if request.user.is_authenticated:
        wish = Wishlist.objects.filter(user=request.user).first()
        if wish:
            wishlist_ids = list(wish.products.values_list('id', flat=True))
    return render(request, 'home.html', {
        'hero': hero,
        'platforms': platforms,
        'on_sale': on_sale,
        'new_releases': new_releases,
        'latest_games': latest_games,
        'wishlist_ids': wishlist_ids,
    })
