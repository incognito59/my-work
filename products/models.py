from django.db import models

class Product(models.Model):
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    image_url = models.CharField(max_length=2083)

    # ✅ New fields for full detail view
    description = models.TextField(blank=True)  # Full product description
    image_2 = models.CharField(max_length=2083, blank=True, null=True)  # Optional second image
    image_3 = models.CharField(max_length=2083, blank=True, null=True)  # Optional third image

    def __str__(self):
        return self.name


class Offer(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    discount = models.FloatField()
