from django.db import models
from .product import Product

class Cart (models.Model):
    username = models.CharField(max_length=100, default='guest')
    product=models.ForeignKey("Product", on_delete=models.CASCADE)
    quantity=models.PositiveIntegerField(default=1)
    price=models.IntegerField(default=0)

    def __str__(self):
        return f"{self.username} - {self.product.name} x {self.quantity}"
