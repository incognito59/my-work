"""
Django Management Command: seed_products
========================================
Usage:
    python manage.py seed_products

Place this file at:
    your_app/management/commands/seed_products.py

Make sure your_app/management/__init__.py and
your_app/management/commands/__init__.py both exist (can be empty).
"""

from django.core.management.base import BaseCommand
from django.utils import timezone
from datetime import timedelta

# 👇 Change 'store' to whatever your app name is that contains Product
from products.models import Product  # ← UPDATE THIS IMPORT


# ============================================================
# ✏️  DEFINE YOUR PRODUCTS HERE
# ============================================================
PRODUCTS = [
    {
        "name": "Wireless Bluetooth Headphones",
        "price": 25000.00,
        "stock": 50,
        "stock_quantity": 50,
        "category": "Electronics",
        "image_url": "https://images.unsplash.com/photo-1505740420928-5e560c06d30e?w=500",
        "description": "High-quality wireless headphones with noise cancellation, 30-hour battery life, and deep bass sound.",
        "image_2": "https://images.unsplash.com/photo-1583394838336-acd977736f90?w=500",
        "image_3": None,
        "sale_price": 19999.00,                          # set to None for no flash sale
        "sale_ends_at": timezone.now() + timedelta(days=3),  # set to None for no flash sale
    },
    {
        "name": "Men's Classic Polo Shirt",
        "price": 7500.00,
        "stock": 120,
        "stock_quantity": 120,
        "category": "Clothing",
        "image_url": "https://images.unsplash.com/photo-1586790170083-2f9ceadc732d?w=500",
        "description": "Premium cotton polo shirt available in multiple colours. Slim fit, breathable fabric, perfect for casual and semi-formal occasions.",
        "image_2": None,
        "image_3": None,
        "sale_price": None,
        "sale_ends_at": None,
    },
    {
        "name": "Stainless Steel Cooking Pot Set (5-piece)",
        "price": 18500.00,
        "stock": 35,
        "stock_quantity": 35,
        "category": "Home",
        "image_url": "https://images.unsplash.com/photo-1556909114-f6e7ad7d3136?w=500",
        "description": "5-piece stainless steel pot set with glass lids. Heat-resistant handles, dishwasher safe, suitable for all cooktops including induction.",
        "image_2": None,
        "image_3": None,
        "sale_price": None,
        "sale_ends_at": None,
    },
    {
        "name": "Yoga Mat (Non-Slip, 6mm)",
        "price": 9000.00,
        "stock": 80,
        "stock_quantity": 80,
        "category": "Sports",
        "image_url": "https://images.unsplash.com/photo-1601925228782-9a5a53b4b73b?w=500",
        "description": "Thick non-slip yoga mat with alignment lines. Eco-friendly TPE material, carry strap included. Ideal for yoga, pilates, and home workouts.",
        "image_2": None,
        "image_3": None,
        "sale_price": 7500.00,
        "sale_ends_at": timezone.now() + timedelta(days=1),
    },
    {
        "name": "Atomic Habits – James Clear",
        "price": 5500.00,
        "stock": 200,
        "stock_quantity": 200,
        "category": "Books",
        "image_url": "https://images.unsplash.com/photo-1544716278-ca5e3f4abd8c?w=500",
        "description": "The #1 New York Times bestseller on building good habits and breaking bad ones. A must-read for personal development.",
        "image_2": None,
        "image_3": None,
        "sale_price": None,
        "sale_ends_at": None,
    },
    {
        "name": "LEGO Classic Creative Bricks (500 pcs)",
        "price": 14000.00,
        "stock": 60,
        "stock_quantity": 60,
        "category": "Toys",
        "image_url": "https://images.unsplash.com/photo-1587654780291-39c9404d746b?w=500",
        "description": "500-piece classic LEGO set for ages 4 and up. Encourages creativity, imagination, and fine motor skill development.",
        "image_2": None,
        "image_3": None,
        "sale_price": None,
        "sale_ends_at": None,
    },
    {
        "name": "USB-C Fast Charger (65W GaN)",
        "price": 11500.00,
        "stock": 90,
        "stock_quantity": 90,
        "category": "Electronics",
        "image_url": "https://images.unsplash.com/photo-1583394293214-0d3a7c36a5b5?w=500",
        "description": "65W GaN compact fast charger compatible with laptops, phones, and tablets. Supports PD 3.0 and QC 4.0. Foldable plug.",
        "image_2": None,
        "image_3": None,
        "sale_price": None,
        "sale_ends_at": None,
    },
    {
        "name": "Women's Running Sneakers",
        "price": 22000.00,
        "stock": 45,
        "stock_quantity": 45,
        "category": "Sports",
        "image_url": "https://images.unsplash.com/photo-1542291026-7eec264c27ff?w=500",
        "description": "Lightweight and responsive running shoes with breathable mesh upper, cushioned insole, and anti-slip rubber outsole.",
        "image_2": "https://images.unsplash.com/photo-1595950653106-6c9ebd614d3a?w=500",
        "image_3": None,
        "sale_price": None,
        "sale_ends_at": None,
    },
    # ----------------------------------------------------------------
    # ➕ ADD MORE PRODUCTS BELOW IN THE SAME FORMAT
    # ----------------------------------------------------------------
]


# ============================================================
# COMMAND LOGIC — no need to edit below this line
# ============================================================
class Command(BaseCommand):
    help = "Seed the database with predefined products"

    def add_arguments(self, parser):
        parser.add_argument(
            "--clear",
            action="store_true",
            help="Delete ALL existing products before seeding (use with caution!)",
        )
        parser.add_argument(
            "--skip-existing",
            action="store_true",
            default=True,
            help="Skip products that already exist by name (default: True)",
        )

    def handle(self, *args, **options):
        if options["clear"]:
            count = Product.objects.count()
            Product.objects.all().delete()
            self.stdout.write(self.style.WARNING(f"🗑️  Deleted {count} existing product(s)."))

        created_count = 0
        skipped_count = 0

        for data in PRODUCTS:
            name = data["name"]

            if not options["clear"] and Product.objects.filter(name=name).exists():
                self.stdout.write(self.style.WARNING(f"  ⏭️  Skipped (already exists): {name}"))
                skipped_count += 1
                continue

            Product.objects.create(
                name=name,
                price=data["price"],
                stock=data["stock"],
                stock_quantity=data.get("stock_quantity"),
                category=data["category"],
                image_url=data["image_url"],
                description=data.get("description", ""),
                image_2=data.get("image_2"),
                image_3=data.get("image_3"),
                sale_price=data.get("sale_price"),
                sale_ends_at=data.get("sale_ends_at"),
            )
            self.stdout.write(self.style.SUCCESS(f"  ✅ Created: {name}"))
            created_count += 1

        self.stdout.write(
            self.style.SUCCESS(
                f"\n🎉 Done! {created_count} product(s) created, {skipped_count} skipped."
            )
        )