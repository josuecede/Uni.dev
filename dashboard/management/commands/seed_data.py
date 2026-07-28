import io
import os
import random
import urllib.request
from datetime import date, timedelta
from django.core.management.base import BaseCommand
from django.core.files.base import ContentFile
from django.conf import settings
from PIL import Image, ImageDraw

from dashboard.models import Platform, Genre, Category, Product, ProductImage
from users.models import CustomUser

COVER_URLS = {
    'Cyberpunk 2077': 'https://upload.wikimedia.org/wikipedia/en/9/9f/Cyberpunk_2077_box_art.jpg',
    'Elden Ring': 'https://upload.wikimedia.org/wikipedia/en/b/b9/Elden_Ring_Box_art.jpg',
    'God of War Ragnarök': 'https://upload.wikimedia.org/wikipedia/en/e/ee/God_of_War_Ragnar%C3%B6k_cover.jpg',
    'The Legend of Zelda: Tears of the Kingdom': 'https://upload.wikimedia.org/wikipedia/en/f/fb/The_Legend_of_Zelda_Tears_of_the_Kingdom_cover.jpg',
    'Red Dead Redemption 2': 'https://upload.wikimedia.org/wikipedia/en/4/44/Red_Dead_Redemption_II.jpg',
    'Baldur\'s Gate 3': 'https://upload.wikimedia.org/wikipedia/en/1/12/Baldur%27s_Gate_3_cover_art.jpg',
    'Forza Motorsport': 'https://upload.wikimedia.org/wikipedia/en/7/7e/Forza_Motorsport_%282023%29_cover_art.png',
    'Horizon Forbidden West': 'https://upload.wikimedia.org/wikipedia/en/6/69/Horizon_Forbidden_West_cover_art.jpg',
    'Starfield': 'https://upload.wikimedia.org/wikipedia/en/6/6d/Bethesda_Starfield.jpg',
    'Mortal Kombat 1': 'https://upload.wikimedia.org/wikipedia/en/5/5b/Mortal_Kombat_1_key_art.jpeg',
    'Gran Turismo 7': 'https://upload.wikimedia.org/wikipedia/en/1/14/Gran_Turismo_7_cover_art.jpg',
    'Stray': 'https://upload.wikimedia.org/wikipedia/en/f/f1/Stray_cover_art.jpg',
    'Hollow Knight': 'https://upload.wikimedia.org/wikipedia/en/d/de/Hollow_Knight_2026_cover_art.jpg',
    'Celeste': 'https://upload.wikimedia.org/wikipedia/commons/0/0f/Celeste_box_art_full.png',
    'Grand Theft Auto V': 'https://upload.wikimedia.org/wikipedia/en/a/a5/Grand_Theft_Auto_V.png',
    'Fortnite': 'https://static.wikia.nocookie.net/fortnite/images/a/a6/Fortnite_%28Update_v41.20%29_-_Cover_Art_-_Fortnite.jpg/revision/latest?cb=20260716084407',
    'Genshin Impact': 'https://images.launchbox-app.com/1e6e82fb-e45f-4d85-9875-3fc893fa3495.jpg',
    'Spider-Man 2': 'https://upload.wikimedia.org/wikipedia/en/0/0f/SpiderMan2PS5BoxArt.jpeg',
    'Call of Duty: Modern Warfare III': 'https://upload.wikimedia.org/wikipedia/en/f/f6/MWIII_Cover_Art.png',
    'FIFA 24': 'https://upload.wikimedia.org/wikipedia/en/b/b3/EA_FC24_Cover.jpg',
    'Resident Evil 4 Remake': 'https://upload.wikimedia.org/wikipedia/en/d/df/Resident_Evil_4_remake_cover_art.jpg',
    'Assassin\'s Creed Mirage': 'https://upload.wikimedia.org/wikipedia/en/2/23/Assassin%27s_Creed_Mirage_cover.jpeg',
    'Hogwarts Legacy': 'https://upload.wikimedia.org/wikipedia/en/f/fb/Hogwarts_legacyboxart.png',
    'Stardew Valley': 'https://cdn.cloudflare.steamstatic.com/steam/apps/413150/library_600x900.jpg',
    'Counter-Strike 2': 'https://upload.wikimedia.org/wikipedia/en/f/f2/CS2_Cover_Art.jpg',
}

PLATFORMS = [
    {'name': 'PC', 'slug': 'pc', 'icon': 'bi-pc-display', 'color': '#1a1a2e'},
    {'name': 'PlayStation 5', 'slug': 'ps5', 'icon': 'bi-playstation', 'color': '#003791'},
    {'name': 'Xbox Series X|S', 'slug': 'xbox', 'icon': 'bi-xbox', 'color': '#107c10'},
    {'name': 'Nintendo Switch', 'slug': 'switch', 'icon': 'bi-nintendo-switch', 'color': '#e60012'},
    {'name': 'Android', 'slug': 'android', 'icon': 'bi-phone', 'color': '#3ddc84'},
]

GENRES = [
    {'name': 'Acción', 'slug': 'accion'},
    {'name': 'Aventura', 'slug': 'aventura'},
    {'name': 'RPG', 'slug': 'rpg'},
    {'name': 'Shooter', 'slug': 'shooter'},
    {'name': 'Estrategia', 'slug': 'estrategia'},
    {'name': 'Deportes', 'slug': 'deportes'},
    {'name': 'Carreras', 'slug': 'carreras'},
    {'name': 'Simulación', 'slug': 'simulacion'},
    {'name': 'Terror', 'slug': 'terror'},
    {'name': 'Mundo Abierto', 'slug': 'mundo-abierto'},
]

CATEGORIES = [
    {'name': 'Juegos Premium', 'description': 'Juegos de pago con contenido completo'},
    {'name': 'Free to Play', 'description': 'Juegos gratuitos con micropagos'},
    {'name': 'Indie', 'description': 'Juegos independientes'},
    {'name': 'Clásicos', 'description': 'Juegos retro y clásicos'},
    {'name': 'VR', 'description': 'Realidad virtual'},
]

GAMES = [
    {'name': 'Cyberpunk 2077', 'description': 'Sumérgete en Night City, una megalópolis obsesionada con el poder, el glamour y las modificaciones corporales. Juega como V, un mercenario forajido en busca de un implante único que es la llave de la inmortalidad.', 'price': 59.99, 'discount': 40, 'developer': 'CD Projekt Red', 'publisher': 'CD Projekt', 'release': '2020-12-10', 'rating': 8.6, 'video': 'https://www.youtube.com/embed/8X2kIfS6fb8', 'platforms': ['pc', 'ps5', 'xbox'], 'genres': ['rpg', 'accion', 'mundo-abierto'], 'category': 'Juegos Premium'},
    {'name': 'Elden Ring', 'description': 'Álzate, Sinluz, y adéntrate en las Tierras Intermedias. Un mundo de fantasía épica creado por Hidetaka Miyazaki y George R.R. Martin.', 'price': 69.99, 'discount': 25, 'developer': 'FromSoftware', 'publisher': 'Bandai Namco', 'release': '2022-02-25', 'rating': 9.8, 'video': 'https://www.youtube.com/embed/AKXiKBvzpGM', 'platforms': ['pc', 'ps5', 'xbox'], 'genres': ['rpg', 'accion', 'aventura'], 'category': 'Juegos Premium'},
    {'name': 'God of War Ragnarök', 'description': 'Kratos y Atreus se embarcan en un viaje épico a través de los nueve reinos en busca de respuestas.', 'price': 69.99, 'discount': 20, 'developer': 'Santa Monica Studio', 'publisher': 'Sony Interactive Entertainment', 'release': '2022-11-09', 'rating': 9.6, 'video': 'https://www.youtube.com/embed/EE-4GvjKc5Y', 'platforms': ['ps5', 'pc'], 'genres': ['accion', 'aventura'], 'category': 'Juegos Premium'},
    {'name': 'The Legend of Zelda: Tears of the Kingdom', 'description': 'Explora un mundo lleno de maravillas mientras Link descubre los secretos de Hyrule en esta épica aventura.', 'price': 69.99, 'discount': 10, 'developer': 'Nintendo EPD', 'publisher': 'Nintendo', 'release': '2023-05-12', 'rating': 9.9, 'video': 'https://www.youtube.com/embed/uHGShqcAIlI', 'platforms': ['switch'], 'genres': ['aventura', 'mundo-abierto'], 'category': 'Juegos Premium'},
    {'name': 'Red Dead Redemption 2', 'description': 'Vive la épica historia del forajido Arthur Morgan en el Salvaje Oeste. Un mundo abierto inmersivo con una narrativa inolvidable.', 'price': 59.99, 'discount': 50, 'developer': 'Rockstar Games', 'publisher': 'Rockstar Games', 'release': '2018-10-26', 'rating': 9.7, 'video': 'https://www.youtube.com/embed/eaW0tYpxyp0', 'platforms': ['pc', 'ps5', 'xbox'], 'genres': ['accion', 'aventura', 'mundo-abierto'], 'category': 'Juegos Premium'},
    {'name': 'Spider-Man 2', 'description': 'Peter Parker y Miles Morales se unen para enfrentar a Venom y proteger la ciudad de Nueva York.', 'price': 69.99, 'discount': 15, 'developer': 'Insomniac Games', 'publisher': 'Sony Interactive Entertainment', 'release': '2023-10-20', 'rating': 9.5, 'video': 'https://www.youtube.com/embed/nq2GXiGBqjI', 'platforms': ['ps5'], 'genres': ['accion', 'aventura', 'mundo-abierto'], 'category': 'Juegos Premium'},
    {'name': 'Baldur\'s Gate 3', 'description': 'Reúne a tu grupo y regresa a los Reinos Olvidados en esta historia de amistad, traición y sacrificio.', 'price': 59.99, 'discount': 10, 'developer': 'Larian Studios', 'publisher': 'Larian Studios', 'release': '2023-08-03', 'rating': 9.9, 'video': 'https://www.youtube.com/embed/1T22wNmf0Mg', 'platforms': ['pc', 'ps5', 'xbox'], 'genres': ['rpg', 'estrategia'], 'category': 'Juegos Premium'},
    {'name': 'Call of Duty: Modern Warfare III', 'description': 'La amenaza continúa mientras el Capitán Price y la Task Force 141 enfrentan a Vladimir Makarov.', 'price': 69.99, 'discount': 30, 'developer': 'Sledgehammer Games', 'publisher': 'Activision', 'release': '2023-11-10', 'rating': 7.8, 'video': 'https://www.youtube.com/embed/xfDk7YvVjPk', 'platforms': ['pc', 'ps5', 'xbox'], 'genres': ['shooter', 'accion'], 'category': 'Juegos Premium'},
    {'name': 'FIFA 24', 'description': 'La experiencia de fútbol más auténtica con nuevas mecánicas de juego, modos mejorados y los mejores equipos del mundo.', 'price': 69.99, 'discount': 35, 'developer': 'EA Sports', 'publisher': 'Electronic Arts', 'release': '2024-09-27', 'rating': 8.5, 'video': 'https://www.youtube.com/embed/V2OwTw8K0Vg', 'platforms': ['pc', 'ps5', 'xbox', 'switch'], 'genres': ['deportes'], 'category': 'Juegos Premium'},
    {'name': 'Forza Motorsport', 'description': 'Vive la velocidad con el simulador de carreras más avanzado. Más de 500 coches y 20 circuitos.', 'price': 69.99, 'discount': 30, 'developer': 'Turn 10 Studios', 'publisher': 'Xbox Game Studios', 'release': '2023-10-10', 'rating': 9.2, 'video': 'https://www.youtube.com/embed/0Y_-iM5nXqI', 'platforms': ['pc', 'xbox'], 'genres': ['carreras', 'simulacion'], 'category': 'Juegos Premium'},
    {'name': 'Horizon Forbidden West', 'description': 'Aloy se aventura en el Oeste Prohibido para descubrir los secretos que amenazan la vida en la Tierra.', 'price': 59.99, 'discount': 35, 'developer': 'Guerrilla Games', 'publisher': 'Sony Interactive Entertainment', 'release': '2022-02-18', 'rating': 9.3, 'video': 'https://www.youtube.com/embed/Lq594XmpPBg', 'platforms': ['ps5', 'pc'], 'genres': ['accion', 'aventura', 'rpg'], 'category': 'Juegos Premium'},
    {'name': 'Resident Evil 4 Remake', 'description': 'Revive la icónica aventura de survival horror con gráficos renovados y nuevas mecánicas de juego.', 'price': 59.99, 'discount': 40, 'developer': 'Capcom', 'publisher': 'Capcom', 'release': '2023-03-24', 'rating': 9.4, 'video': 'https://www.youtube.com/embed/9s6ZgC6S0ys', 'platforms': ['pc', 'ps5', 'xbox'], 'genres': ['terror', 'accion', 'aventura'], 'category': 'Juegos Premium'},
    {'name': 'Starfield', 'description': 'Explora el vasto espacio exterior en esta épica aventura de rol de Bethesda Game Studios.', 'price': 69.99, 'discount': 30, 'developer': 'Bethesda Game Studios', 'publisher': 'Bethesda Softworks', 'release': '2023-09-06', 'rating': 8.5, 'video': 'https://www.youtube.com/embed/zmb2FVGvn8Q', 'platforms': ['pc', 'xbox'], 'genres': ['rpg', 'aventura', 'mundo-abierto'], 'category': 'Juegos Premium'},
    {'name': 'Mortal Kombat 1', 'description': 'Un nuevo universo de kombate te espera. Gráficos impresionantes y un sistema de lucha revolucionario.', 'price': 69.99, 'discount': 40, 'developer': 'NetherRealm Studios', 'publisher': 'Warner Bros. Games', 'release': '2023-09-19', 'rating': 8.7, 'video': 'https://www.youtube.com/embed/UZ6eFEjFfJ0', 'platforms': ['pc', 'ps5', 'xbox', 'switch'], 'genres': ['accion'], 'category': 'Juegos Premium'},
    {'name': 'Assassin\'s Creed Mirage', 'description': 'Vive la historia de Basim en el Bagdad del siglo IX en esta vuelta a las raíces de la saga.', 'price': 49.99, 'discount': 40, 'developer': 'Ubisoft Bordeaux', 'publisher': 'Ubisoft', 'release': '2023-10-05', 'rating': 8.8, 'video': 'https://www.youtube.com/embed/x55hSHiIl2I', 'platforms': ['pc', 'ps5', 'xbox'], 'genres': ['accion', 'aventura'], 'category': 'Juegos Premium'},
    {'name': 'Hogwarts Legacy', 'description': 'Vive tu propia aventura en el Mundo Mágico. Explora Hogwarts y descubre secretos ocultos.', 'price': 59.99, 'discount': 40, 'developer': 'Avalanche Software', 'publisher': 'Warner Bros. Games', 'release': '2023-02-10', 'rating': 9.0, 'video': 'https://www.youtube.com/embed/1O6Qstncpnc', 'platforms': ['pc', 'ps5', 'xbox', 'switch'], 'genres': ['rpg', 'aventura', 'mundo-abierto'], 'category': 'Juegos Premium'},
    {'name': 'Gran Turismo 7', 'description': 'La experiencia de conducción definitiva con más de 400 coches y 100 circuitos.', 'price': 69.99, 'discount': 30, 'developer': 'Polyphony Digital', 'publisher': 'Sony Interactive Entertainment', 'release': '2022-03-04', 'rating': 9.1, 'video': 'https://www.youtube.com/embed/a3Z7zEcYnOM', 'platforms': ['ps5'], 'genres': ['carreras', 'simulacion'], 'category': 'Juegos Premium'},
    {'name': 'Stray', 'description': 'Juega como un gato callejero en una ciudad cyberpunk llena de robots y misterios.', 'price': 29.99, 'discount': 20, 'developer': 'BlueTwelve Studio', 'publisher': 'Annapurna Interactive', 'release': '2022-07-19', 'rating': 9.0, 'video': 'https://www.youtube.com/embed/38GZ3cD7XG0', 'platforms': ['pc', 'ps5', 'xbox', 'switch'], 'genres': ['aventura', 'indie'], 'category': 'Indie'},
    {'name': 'Hollow Knight', 'description': 'Adéntrate en el reino de Hallownest, un mundo subterráneo lleno de insectos y misterios.', 'price': 14.99, 'discount': 30, 'developer': 'Team Cherry', 'publisher': 'Team Cherry', 'release': '2017-02-24', 'rating': 9.5, 'video': 'https://www.youtube.com/embed/UAO2urG23S4', 'platforms': ['pc', 'ps5', 'xbox', 'switch'], 'genres': ['aventura', 'accion', 'indie'], 'category': 'Indie'},
    {'name': 'Stardew Valley', 'description': 'Deja la ciudad y vive tus sueños agrícolas en el campo. Cultiva, cría animales y haz amigos.', 'price': 14.99, 'discount': 0, 'developer': 'ConcernedApe', 'publisher': 'ConcernedApe', 'release': '2016-02-26', 'rating': 9.8, 'video': 'https://www.youtube.com/embed/ot7u5Vl3lJc', 'platforms': ['pc', 'ps5', 'xbox', 'switch', 'android'], 'genres': ['simulacion', 'indie'], 'category': 'Indie'},
    {'name': 'Celeste', 'description': 'Ayuda a Madeline a escalar la Montaña Celeste en este desafiante y conmovedor juego de plataformas.', 'price': 19.99, 'discount': 30, 'developer': 'Maddy Makes Games', 'publisher': 'Maddy Makes Games', 'release': '2018-01-25', 'rating': 9.6, 'video': 'https://www.youtube.com/embed/70d9irlxiB4', 'platforms': ['pc', 'ps5', 'xbox', 'switch'], 'genres': ['accion', 'indie'], 'category': 'Indie'},
    {'name': 'Counter-Strike 2', 'description': 'El shooter táctico por excelencia renace con gráficos mejorados y nuevas mecánicas.', 'price': 0, 'discount': 0, 'developer': 'Valve', 'publisher': 'Valve', 'release': '2023-09-27', 'rating': 9.1, 'video': 'https://www.youtube.com/embed/8yrX-piJuHM', 'platforms': ['pc'], 'genres': ['shooter', 'accion', 'estrategia'], 'category': 'Free to Play'},
    {'name': 'Fortnite', 'description': 'El battle royale más popular del mundo. Construye, lucha y sé el último en pie.', 'price': 0, 'discount': 0, 'developer': 'Epic Games', 'publisher': 'Epic Games', 'release': '2017-07-25', 'rating': 8.9, 'video': 'https://www.youtube.com/embed/WJW-bzXZM8M', 'platforms': ['pc', 'ps5', 'xbox', 'switch', 'android'], 'genres': ['shooter', 'accion'], 'category': 'Free to Play'},
    {'name': 'Genshin Impact', 'description': 'Explora el mundo de Teyvat y descubre sus secretos en este RPG de acción gratuito.', 'price': 0, 'discount': 0, 'developer': 'miHoYo', 'publisher': 'miHoYo', 'release': '2020-09-28', 'rating': 9.3, 'video': 'https://www.youtube.com/embed/HLUY1nICQRY', 'platforms': ['pc', 'ps5', 'android'], 'genres': ['rpg', 'accion', 'mundo-abierto'], 'category': 'Free to Play'},
    {'name': 'Grand Theft Auto V', 'description': 'Tres criminales, una ciudad. Vive la historia de Michael, Franklin y Trevor en Los Santos.', 'price': 29.99, 'discount': 50, 'developer': 'Rockstar North', 'publisher': 'Rockstar Games', 'release': '2013-09-17', 'rating': 9.8, 'video': 'https://www.youtube.com/embed/hvoD7ehZPcM', 'platforms': ['pc', 'ps5', 'xbox'], 'genres': ['accion', 'aventura', 'mundo-abierto'], 'category': 'Clásicos'},
]

COLORS = [
    '#6c5ce7', '#00cec9', '#fd79a8', '#e17055', '#00b894',
    '#fdcb6e', '#e84393', '#6ab04c', '#eb4d4b', '#686de0',
    '#30336b', '#be2edd', '#4834d4', '#130f40', '#535c68',
    '#2ecc71', '#3498db', '#9b59b6', '#1abc9c', '#e67e22',
    '#34495e', '#16a085', '#27ae60', '#2980b9', '#8e44ad',
]

PLACEHOLDER_COLORS = [
    '#1a1a2e', '#16213e', '#0f3460', '#e94560', '#533483',
    '#e07c24', '#2d4059', '#ea5455', '#f07b3f', '#1b1717',
    '#810000', '#630000', '#222831', '#30475e', '#f05454',
    '#2c3e50', '#8e44ad', '#16a085', '#c0392b', '#d35400',
    '#2980b9', '#27ae60', '#f39c12', '#7f8c8d', '#2c3e50',
]


def download_image(url, timeout=5):
    try:
        req = urllib.request.Request(url, headers={'User-Agent': 'Mozilla/5.0'})
        with urllib.request.urlopen(req, timeout=timeout) as resp:
            return resp.read()
    except Exception:
        return None


def generate_placeholder(color, size=(400, 225)):
    img = Image.new('RGB', size, color=color)
    draw = ImageDraw.Draw(img)
    r, g, b = int(color[1:3], 16), int(color[3:5], 16), int(color[5:7], 16)
    accent = (min(255, r + 40), min(255, g + 40), min(255, b + 40))
    draw.ellipse([size[0]//4, size[1]//4, size[0]*3//4, size[1]*3//4], fill=accent)
    draw.rectangle([size[0]//3, size[1]//3, size[0]*2//3, size[1]*2//3], fill=None, outline='white', width=3)
    buf = io.BytesIO()
    img.save(buf, format='PNG')
    return buf.getvalue()


def get_image_data(game_name, color):
    url = COVER_URLS.get(game_name)
    if url:
        data = download_image(url)
        if data:
            return data
    return generate_placeholder(color)


def get_gallery_images(color):
    imgs = []
    for _ in range(4):
        imgs.append(generate_placeholder(color, (200, 112)))
    return imgs


class Command(BaseCommand):
    help = 'Seed database with platforms, genres, categories, and games'

    def handle(self, *args, **options):
        self.stdout.write('Creando plataformas...')
        for data in PLATFORMS:
            Platform.objects.get_or_create(slug=data['slug'], defaults=data)
            self.stdout.write(f'  + {data["name"]}')

        self.stdout.write('Creando géneros...')
        for data in GENRES:
            Genre.objects.get_or_create(slug=data['slug'], defaults=data)
            self.stdout.write(f'  + {data["name"]}')

        self.stdout.write('Creando categorías...')
        for data in CATEGORIES:
            Category.objects.get_or_create(name=data['name'], defaults=data)
            self.stdout.write(f'  + {data["name"]}')

        self.stdout.write('Creando juegos...')
        for i, game_data in enumerate(GAMES):
            color = COLORS[i % len(COLORS)]
            cat = Category.objects.get(name=game_data['category'])
            product, created = Product.objects.get_or_create(
                name=game_data['name'],
                defaults={
                    'description': game_data['description'],
                    'price': game_data['price'],
                    'discount_percent': game_data['discount'],
                    'stock': random.randint(50, 500),
                    'category': cat,
                    'developer': game_data['developer'],
                    'publisher': game_data['publisher'],
                    'release_date': game_data['release'],
                    'rating': game_data['rating'],
                    'video_url': game_data['video'],
                    'is_active': True,
                    'is_featured': i < 6,
                    'is_new_release': i < 3,
                    'format': 'DIGITAL',
                }
            )

            img_data = get_image_data(game_data['name'], color)
            product.image.save(f'product_{product.id}.png', ContentFile(img_data))
            product.save()
            label = '+' if created else '~'
            self.stdout.write(f'  {label} {game_data["name"]} (${game_data["price"]})')

            product.platforms.set([Platform.objects.get(slug=s) for s in game_data['platforms']])
            product.genres.set([Genre.objects.get(slug=s) for s in game_data['genres']])

            existing_gallery_count = product.images.count()
            if existing_gallery_count < 4:
                for gi in range(existing_gallery_count, 4):
                    img_data = generate_placeholder(PLACEHOLDER_COLORS[(i + gi) % len(PLACEHOLDER_COLORS)], (200, 112))
                    pi = ProductImage(product=product, is_primary=gi == 0)
                    pi.image.save(f'product_{product.id}_gallery_{gi}.png', ContentFile(img_data))
                    pi.save()

        admin_user = CustomUser.objects.filter(username='admin').first()
        if admin_user:
            admin_user.first_name = 'Josue'
            admin_user.last_name = 'Cedeño'
            admin_user.email = 'admin@gamestore.com'
            admin_user.phone_number = '+593 98 765 4321'
            admin_user.bio = 'Administrador de GameStore. Apasionado por los videojuegos y la tecnología.'
            admin_user.address = 'Manta, Ecuador'
            admin_user.role = 'ADMIN'
            admin_user.save()
            self.stdout.write(f'  + Perfil de admin actualizado')

        self.stdout.write(self.style.SUCCESS('Seed completado exitosamente!'))
