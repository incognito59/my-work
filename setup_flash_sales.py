#!/usr/bin/env python
"""
Flash Sale Timer - Demo/Test Setup Script

This script demonstrates how to set up flash sales for products programmatically.
Run this from the Django shell:
    python manage.py shell < setup_flash_sales.py

Or import and run individual functions as needed.
"""

from datetime import datetime, timedelta
from django.utils import timezone
from products.models import Product

def setup_demo_flash_sales():
    """
    Set up demo flash sales for the first 3 products in the database.
    This is useful for testing the flash sale timer functionality.
    """
    products = Product.objects.all()[:3]
    
    if not products.exists():
        print("❌ No products found. Please add products first.")
        return
    
    # Set different sale durations for each product to demonstrate timer variations
    sale_configs = [
        {
            'discount_percent': 30,
            'hours_until_sale_ends': 1,  # Urgent - less than 1 hour
            'label': 'Last Minute Deal'
        },
        {
            'discount_percent': 25,
            'hours_until_sale_ends': 12,  # Warning - less than 1 day
            'label': '12-Hour Flash Deal'
        },
        {
            'discount_percent': 20,
            'hours_until_sale_ends': 48,  # Normal - 2 days
            'label': '2-Day Sale'
        }
    ]
    
    for i, product in enumerate(products):
        config = sale_configs[i % len(sale_configs)]
        
        # Calculate sale price based on discount percentage
        discount = product.price * (config['discount_percent'] / 100)
        sale_price = product.price - discount
        
        # Calculate sale end time
        sale_ends_at = timezone.now() + timedelta(hours=config['hours_until_sale_ends'])
        
        # Update product
        product.sale_price = sale_price
        product.sale_ends_at = sale_ends_at
        product.save()
        
        print(f"✅ {product.name}")
        print(f"   Original Price: ₦{product.price:.2f}")
        print(f"   Sale Price: ₦{sale_price:.2f}")
        print(f"   Discount: {config['discount_percent']}%")
        print(f"   Sale Ends: {sale_ends_at.strftime('%Y-%m-%d %H:%M:%S')}")
        print(f"   Status: {config['label']}")
        print()


def create_specific_flash_sale(product_id, sale_price, hours_until_end):
    """
    Create a flash sale for a specific product.
    
    Args:
        product_id: The ID of the product
        sale_price: The discounted price (e.g., 5000)
        hours_until_end: How many hours until the sale ends (e.g., 2)
    
    Example:
        create_specific_flash_sale(1, 7000, 2)
    """
    try:
        product = Product.objects.get(id=product_id)
        product.sale_price = sale_price
        product.sale_ends_at = timezone.now() + timedelta(hours=hours_until_end)
        product.save()
        
        discount_percent = product.discount_percentage
        print(f"✅ Flash Sale Created!")
        print(f"   Product: {product.name}")
        print(f"   Original: ₦{product.price:.2f} → Sale: ₦{sale_price:.2f}")
        print(f"   Discount: {discount_percent}%")
        print(f"   Ends: {product.sale_ends_at.strftime('%Y-%m-%d %H:%M:%S')}")
        
    except Product.DoesNotExist:
        print(f"❌ Product with ID {product_id} not found.")


def end_flash_sale(product_id):
    """
    End a flash sale for a specific product.
    
    Args:
        product_id: The ID of the product
    
    Example:
        end_flash_sale(1)
    """
    try:
        product = Product.objects.get(id=product_id)
        product.sale_price = None
        product.sale_ends_at = None
        product.save()
        
        print(f"✅ Flash Sale Ended!")
        print(f"   Product: {product.name}")
        print(f"   Price reset to: ₦{product.price:.2f}")
        
    except Product.DoesNotExist:
        print(f"❌ Product with ID {product_id} not found.")


def list_active_flash_sales():
    """
    List all products that currently have active flash sales.
    """
    active_sales = [p for p in Product.objects.all() if p.has_active_sale]
    
    if not active_sales:
        print("No active flash sales.")
        return
    
    print(f"📊 Active Flash Sales ({len(active_sales)} products)")
    print("=" * 70)
    
    for product in active_sales:
        remaining = product.sale_ends_at - timezone.now()
        hours = remaining.total_seconds() / 3600
        
        print(f"\n{product.name}")
        print(f"  Original Price: ₦{product.price:.2f}")
        print(f"  Sale Price: ₦{product.sale_price:.2f}")
        print(f"  Discount: {product.discount_percentage}%")
        print(f"  Time Remaining: {hours:.1f} hours")
        print(f"  Ends: {product.sale_ends_at.strftime('%Y-%m-%d %H:%M:%S')}")


def list_expired_sales():
    """
    List products that had sales but the sale has now expired.
    """
    expired = []
    for product in Product.objects.all():
        if product.sale_price and product.sale_ends_at:
            if product.sale_ends_at <= timezone.now():
                expired.append(product)
    
    if not expired:
        print("No expired sales.")
        return
    
    print(f"⏰ Expired Sales ({len(expired)} products)")
    print("=" * 70)
    
    for product in expired:
        print(f"\n{product.name}")
        print(f"  Sale ended: {product.sale_ends_at.strftime('%Y-%m-%d %H:%M:%S')}")


def cleanup_expired_sales():
    """
    Remove sale price and end time from all products with expired sales.
    """
    count = 0
    for product in Product.objects.all():
        if product.sale_price and product.sale_ends_at:
            if product.sale_ends_at <= timezone.now():
                product.sale_price = None
                product.sale_ends_at = None
                product.save()
                count += 1
    
    if count > 0:
        print(f"✅ Cleaned up {count} expired sales.")
    else:
        print("No expired sales to clean up.")


# Example usage when running this script
if __name__ == "__main__":
    print("⚡ Flash Sale Timer - Setup Helper\n")
    
    # Uncomment the function you want to run:
    
    # Setup demo flash sales
    # setup_demo_flash_sales()
    
    # List active sales
    list_active_flash_sales()
    
    # List expired sales
    # list_expired_sales()
    
    # Create a specific flash sale
    # create_specific_flash_sale(product_id=1, sale_price=5000, hours_until_end=2)
    
    # End a flash sale
    # end_flash_sale(product_id=1)
    
    # Cleanup expired sales
    # cleanup_expired_sales()
