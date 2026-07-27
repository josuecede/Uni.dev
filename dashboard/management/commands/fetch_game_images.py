import urllib.request, urllib.error, json, os
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from dashboard.models import Product

GAMES = {
    "Cyberpunk 2077": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1091500/capsule_616x353.jpg",
    "Elden Ring": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1245620/capsule_616x353.jpg",
    "The Legend of Zelda": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/105600/capsule_616x353.jpg",
    "God of War Ragnarok": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2322010/capsule_616x353.jpg",
    "Resident Evil 4": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2050650/capsule_616x353.jpg",
    "FC 25": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2195250/capsule_616x353.jpg",
    "Hogwarts Legacy": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/990080/capsule_616x353.jpg",
    "Starfield": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1716740/capsule_616x353.jpg",
    "Ark": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/346110/capsule_616x353.jpg",
    "Ark ascendan": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/2399830/capsule_616x353.jpg",
}

class Command(BaseCommand):
    help = "Download game images from Steam CDN"

    def handle(self, *args, **options):
        for product in Product.objects.all():
            url = GAMES.get(product.name)
            if not url:
                self.stdout.write(self.style.WARNING(f"No URL for {product.name}"))
                continue
            try:
                req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
                data = urllib.request.urlopen(req, timeout=15).read()
                ext = os.path.splitext(url.split("/")[-1])[0]
                product.image.save(f"{ext}.jpg", ContentFile(data), save=True)
                self.stdout.write(self.style.SUCCESS(f"Set image for {product.name}"))
            except Exception as e:
                self.stdout.write(self.style.ERROR(f"Failed for {product.name}: {e}"))
