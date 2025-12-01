import uuid

from django.db import models
from django.conf import settings

class Collection(models.Model):
    title = models.CharField(max_length=100)

    def __str__(self):
        return self.title

class Product(models.Model):
    title = models.CharField(max_length=100)
    description = models.TextField()
    price = models.DecimalField(decimal_places=2, max_digits=10)
    updated_at = models.DateTimeField(auto_now=True) #auto_now_add=True --- Updates the time once at update.
    inventory = models.PositiveIntegerField()
    collection = models.ForeignKey(Collection, on_delete=models.CASCADE, related_name='collection')

    def __str__(self):
        return self.title

class ProductImage(models.Model):
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='product_images')
    image = models.ImageField(upload_to='store/images')

class Cart(models.Model):
    cart_id = models.UUIDField(default=uuid.uuid4, editable=False, primary_key=True)
    created_at = models.DateTimeField(auto_now_add=True)

class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()

    class Meta:
        unique_together = ('cart', 'product')

class Order(models.Model):
    ORDER_STATUS = (
        ('P', 'Pending'),
        ('C', 'Completed'),
        ('F', 'Failed'),
    )
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.PROTECT)
    placed_at = models.DateTimeField(auto_now_add=True)
    status = models.CharField(max_length=1, choices=ORDER_STATUS, default='P')
    cart = models.ForeignKey(Cart, on_delete=models.PROTECT)

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField()
    unit_price = models.DecimalField(decimal_places=2, max_digits=6)

class ReviewProduct(models.Model):
    name = models.CharField(max_length=100)
    review = models.TextField()
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)