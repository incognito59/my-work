# Django Database Learning Guide

## Why database knowledge is important in Django

Django is a web framework that is built around database-backed applications. In your Retail-Logistics project, almost everything depends on data:

- Products, prices, stock, and flash sale dates are stored in the database.
- User carts, orders, addresses, and payment methods are stored in the database.
- Coupons, discount codes, notifications, and support tickets are database records.
- The `products` app in your project is the main place where these models live.

If you do not understand databases in Django, you will struggle to:

- store new records correctly
- query the right data for lists and filters
- update stock and orders safely
- keep user data consistent and secure
- make changes without breaking the site

## What you need to learn

### 1. Models: the core of Django database work

A model is a Python class that defines a table in the database.
In your `products/models.py`, examples include:

- `Product`
- `Offer`
- `Coupon`
- `Order`
- `OrderItem`
- `Wishlist`
- `AbandonedCart`
- `ProductVariant`
- `UserAddress`
- `PaymentMethod`
- `Notification`

Each field in the model becomes a column in the database.
For example, `Product` has fields such as:

- `name = models.CharField(max_length=255)`
- `price = models.FloatField()`
- `stock = models.IntegerField()`
- `category = models.CharField(max_length=50, choices=CATEGORY_CHOICES)`
- `sale_price = models.FloatField(null=True, blank=True)`
- `sale_ends_at = models.DateTimeField(null=True, blank=True)`

### 2. Relationships: how models connect

Django has fields for connecting models to each other:

- `ForeignKey` — one-to-many relationships
  - `Order` belongs to a `User`
  - `OrderItem` belongs to an `Order`
  - `Wishlist` belongs to `User` and `Product`
- `OneToOneField` — one-to-one relationship
- `ManyToManyField` — many-to-many relationship
  - In your project, `ProductRecommendation` uses `ManyToManyField` to link products that are often bought together.

These relationships are the foundation of an e-commerce app.

### 3. ORM Queries: reading and writing data with Python

Django ORM lets you work with data without writing SQL.
Important query patterns:

- fetch all items:
  - `Product.objects.all()`
- filter items:
  - `Product.objects.filter(category='Electronics')`
- get a single item:
  - `Product.objects.get(id=1)`
- create a record:
  - `Coupon.objects.create(code='SAVE10', discount_value=10)`
- update a record:
  - `product.price = 250; product.save()`

### 4. Migrations: updating the database schema

Migrations are the changes to database tables.
Your project already has many migration files, like `0001_initial.py` through `0011_alter_product_category.py`.

Key commands:

- `python manage.py makemigrations`
- `python manage.py migrate`

These commands track changes so the database matches the models.

### 5. Performance and optimization

For larger apps, correct queries matter.
Important techniques:

- `select_related()` for `ForeignKey` fields to avoid extra queries
- `prefetch_related()` for `ManyToManyField` or reverse relationships
- add indexes on fields used for search or filtering
- only fetch fields you need with `.only()` or `.values()`

Example: if you show product details with related order items, use `select_related('product')`.

### 6. Transactions: keep data safe during checkout

When creating orders and updating stock, use transactions:

```python
from django.db import transaction

with transaction.atomic():
    order = Order.objects.create(...)
    order_item = OrderItem.objects.create(...)
    product.stock -= order_item.quantity
    product.save()
```

If any part fails, the database will roll back all changes.

### 7. Validation and business rules

Models can include methods to check validity:

- `Coupon.is_valid(total)`
- `Product.has_active_sale`
- `Coupon.calculate_discount(subtotal)`

These methods make your app behave correctly when users apply discounts or view a flash sale.

## How this applies to your Retail-Logistics project

Your project is a real e-commerce platform with:

- product inventory
- flash sales and discounts
- user carts and abandoned carts
- orders and order items
- shipping methods
- payment methods
- notifications and support tickets

That means database learning should focus on:

1. understanding `products/models.py`
2. learning how to change models and run migrations
3. writing queries for product search, cart view, and order history
4. making sure stock updates and payments are handled safely

## Recommended learning path

1. Learn the basics of Django models and fields.
2. Learn `ForeignKey`, `ManyToManyField`, and related names.
3. Practice common ORM queries: filter, get, create, update.
4. Learn how migrations work and why they are needed.
5. Study `select_related()` and `prefetch_related()`.
6. Learn transaction handling with `transaction.atomic()`.
7. Apply these concepts to your actual project models.

## Quick study checklist

- [ ] What is a Django model?
- [ ] How does `ForeignKey` differ from `ManyToManyField`?
- [ ] How do I create, update, delete records?
- [ ] What does `makemigrations` do?
- [ ] What does `migrate` do?
- [ ] How do I avoid N+1 database queries?
- [ ] How do I use `transaction.atomic()`?

## Final note

If you want, I can also create a PDF version from this guide. For now I saved the guide as `DATABASE_LEARNING_GUIDE.md` in your project root.
