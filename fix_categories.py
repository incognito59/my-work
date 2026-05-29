import os, django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'mywork.settings')
django.setup()

from products.models import Product

# ID → correct category (manual overrides for mismatched ones)
MANUAL_OVERRIDES = {
    # Phones mismatches
    2567: 'Watches',        # Samsung Galaxy Watch 6 Classic
    2603: 'Home Appliances',# Samsung 65-inch QLED TV
    2610: 'Home Appliances',# Samsung French Door Refrigerator
    2624: 'Electronics',    # Samsung Galaxy Tab S9 Ultra
    2632: 'Electronics',    # Samsung 980 Pro SSD
    2638: 'Fitness',        # Xiaomi Mi Band 8
    2721: 'Watches',        # Xiaomi Watch S3
    2695: 'Accessories',    # PopSockets PopGrip
    2698: 'Accessories',    # Moment Wide Lens for iPhone

    # Sneakers mismatches
    2621: 'Fitness',        # TRX All-in-One Suspension Trainer
    2711: 'Fitness',        # Wahoo KICKR Smart Trainer

    # Home Appliances mismatches
    2622: 'Fitness',        # Kettlebell 20kg
    2647: 'Fitness',        # Blender Bottle Pro Series

    # Electronics mismatches
    2643: 'Fitness',        # Jump Rope Speed Cable
    2716: 'Fitness',        # Polar H10 Heart Rate Monitor

    # Watches override
    2697: 'Accessories',    # Nomad Leather Watch Band
}

CATEGORY_RULES = [
    ('Phones',          ['iphone', 'samsung galaxy', 'tecno', 'infinix', 'xiaomi redmi',
                         'oneplus', 'google pixel', 'motorola', 'nothing phone', 'realme',
                         'huawei mate', 'asus rog phone', 'iphone se']),
    ('Laptops',         ['macbook', 'laptop', 'notebook', 'chromebook', 'thinkpad',
                         'xps 15', 'spectre', 'zephyrus', 'predator', 'razer blade',
                         'surface pro', 'creator z', 'envy x360', 'swift 3', 'hp spectre']),
    ('Gaming',          ['playstation', 'xbox', 'nintendo switch', 'gaming mouse',
                         'gaming keyboard', 'razer deathadder', 'steelseries', 'stream deck',
                         'elgato', 'capture card']),
    ('Watches',         ['watch', 'wristwatch', 'timepiece', 'rolex', 'casio', 'omega',
                         'tag heuer', 'seiko', 'orient', 'timex', 'garmin fenix',
                         'amazfit', 'withings']),
    ('Sneakers',        ['sneaker', 'air max', 'ultraboost', 'jordan', 'dunk low',
                         'stan smith', 'chuck taylor', 'old skool', 'triple s',
                         'yeezy', 'gel-kayano', 'clifton', 'ghost 15', 'speedcross',
                         'nb 574', 'nb 990', 'reebok classic', 'trainer shoe',
                         'running shoe', 'gucci ace', 'lv trainer', 'dior b23',
                         'puma rs', 'converse']),
    ('Electronics',     ['airpods', 'earbuds', 'headphone', 'momentum', 'jabra', 'nothing ear',
                         'beats studio', 'sony wh', 'sennheiser', 'keyboard', 'mouse',
                         'smartwatch', 'powerbank', 'anker power', 'charger', 'cable',
                         'monitor', 'usb-c hub', 'airtag', 'tile mate', 'magsafe',
                         'ipad', 'kindle', 'gopro', 'dji', 'camera', 'alpha a7',
                         'canon eos', 'wacom', 'microphone', 'blue yeti', 'logitech mx',
                         'speaker', 'soundlink', 'jbl', 'sonos', 'marshall', 'wonderboom',
                         'emberton', 'ssd', 'galaxy tab', 'surface', 'smart tv',
                         'philips hue', 'nest', 'ring doorbell', 'arlo', 'august smart lock',
                         'ecobee', 'pixel 8']),
    ('Home Appliances', ['robot vacuum', 'roomba', 'dyson', 'kitchenaid', 'nespresso',
                         'instant pot', 'air fryer', 'refrigerator', 'qled tv', 'oled',
                         'breville', 'cuisinart', 'food processor', 'grill', 'weber']),
    ('Fitness',         ['yoga mat', 'dumbbell', 'resistance band', 'gym bag', 'yoga block',
                         'peloton', 'treadmill', 'whoop', 'theragun', 'hyperice', 'hypervolt',
                         'pull up bar', 'ab roller', 'foam roller', 'rowing machine',
                         'garmin edge', 'garmin hrm', 'fitbit', 'kettlebell',
                         'blender bottle', 'jump rope', 'heart rate monitor',
                         'mi band', 'compression sock', 'trx', 'wahoo', 'bowflex']),
    ('Accessories',     ['wallet', 'handbag', 'sunglasses', 'ray-ban', 'oakley', 'belt',
                         'backpack', 'necklace', 'card holder', 'pocket square',
                         'louis vuitton neverfull', 'gucci dionysus', 'phone case',
                         'popsocket', 'lens for iphone', 'watch band', 'peak design']),
    ('Fashion',         ['suit', 'dress', 'puffer jacket', 'linen shirt', 'jeans', 'biker jacket',
                         'shorts', 'hoodie', 'polo', 'skirt', 'denim jacket', 'bodycon',
                         'maxi', 'bomber jacket', 'turtleneck', 'trench coat', 'chino',
                         'blazer', 'cargo pants', 'stiletto', 'oxford dress shoe',
                         'cashmere', 'silk scarf', 'compression sock', 'sweatshirt']),
    ('Home',            ['frying pan', 'cutting board', 'water bottle', 'mug', 'dinner plate',
                         'bedsheet', 'pillow', 'desk lamp', 'storage bag', 'towel', 'candle']),
    ('Beauty',          ['face cream', 'body lotion', 'lipstick', 'makeup', 'perfume',
                         'beard kit', 'nail polish', 'facial', 'serum', 'shampoo',
                         'skincare', 'grooming', 'brush set', 'sheet mask', 'airwrap',
                         'foundation', 'concealer']),
]

products = Product.objects.all()
updated = 0

for product in products:
    # Manual override takes priority
    if product.id in MANUAL_OVERRIDES:
        product.category = MANUAL_OVERRIDES[product.id]
        product.save(update_fields=['category'])
        print(f"  [OVERRIDE → {product.category}] {product.name}")
        updated += 1
        continue

    name_lower = product.name.lower()
    assigned = 'Other'

    for category, keywords in CATEGORY_RULES:
        if any(kw in name_lower for kw in keywords):
            assigned = category
            break

    product.category = assigned
    product.save(update_fields=['category'])
    print(f"  [{assigned}] {product.name}")
    updated += 1

print(f"\n✅ Done! {updated} products updated.")