from django.db import models
from django.contrib.auth.models import User
from django.templatetags.static import static

class Product(models.Model):
    CATEGORY_CHOICES = [
        ('Electronics', 'Electronics'),
        ('Clothing', 'Clothing'),
        ('Home', 'Home & Kitchen'),
        ('Sports', 'Sports & Outdoors'),
        ('Books', 'Books'),
        ('Toys', 'Toys & Games'),
        ('Other', 'Other'),
    ]
    
    name = models.CharField(max_length=255)
    price = models.FloatField()
    stock = models.IntegerField()
    category = models.CharField(max_length=50, choices=CATEGORY_CHOICES, default='Other')
    image_url = models.CharField("Main Image", max_length=2083)
    description = models.TextField(blank=True)

    # Optional additional image fields
    image_2 = models.CharField("Image 2", max_length=2083, blank=True, null=True)
    image_3 = models.CharField("Image 3", max_length=2083, blank=True, null=True)

    @property
    def image_src(self):
        if self.image_url:
            if self.image_url.startswith(('http://', 'https://', '//')):
                return self.image_url
            return static(self.image_url)
        return 'https://via.placeholder.com/500x350?text=No+Image'

    @property
    def additional_images(self):
        images = []
        for img in [self.image_2, self.image_3]:
            if not img:
                continue
            if img.startswith(('http://', 'https://', '//')):
                images.append(img)
            else:
                images.append(static(img))
        return images

    def __str__(self):
        return self.name

class Offer(models.Model):
    code = models.CharField(max_length=10)
    description = models.CharField(max_length=255)
    discount = models.FloatField()

    def __str__(self):
        return self.code

class Comment(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='comments')
    name = models.CharField(max_length=100)
    text = models.TextField()
    rating = models.IntegerField(choices=[(i, str(i)) for i in range(1, 6)])
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} - {self.rating} stars on {self.product.name}"

class Wishlist(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='wishlist')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} ❤ {self.product.name}"

class Compare(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='compare_list')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)

    def __str__(self):
        return f"{self.user.username} comparing {self.product.name}"

class Order(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    created_at = models.DateTimeField(auto_now_add=True)
    is_paid = models.BooleanField(default=False)

    def __str__(self):
        return f"Order #{self.id} - {self.user.username}"

    @property
    def total(self):
        return sum(item.total_price for item in self.items.all())

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.IntegerField(default=1)

    def __str__(self):
        return f"{self.quantity} x {self.product.name}"

    @property
    def total_price(self):
        return self.product.price * self.quantity