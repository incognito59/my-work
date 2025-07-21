from django.contrib import admin
from .models import Product, Offer


class OfferAdmin(admin.ModelAdmin):
    list_display = ('code', 'discount')


class ProductAdmin(admin.ModelAdmin):
    list_display = ('name', 'price', 'stock')
    fields = ('name', 'price', 'stock', 'description', 'image_url', 'image_2', 'image_3')  # ✅ Show all fields in form


admin.site.register(Offer, OfferAdmin)
admin.site.register(Product, ProductAdmin)
