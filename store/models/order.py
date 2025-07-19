from django.db import models
from django.utils import timezone

class Order(models.Model):
    PAYMENT_CHOICES = [
        ('cod', 'Cash on Delivery'),
        ('online', 'Online Payment'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('shipped', 'Shipped'),
        ('delivered', 'Delivered'),
        ('cancelled', 'Cancelled'),
    ]
    
    username = models.CharField(max_length=100)
    customer_name = models.CharField(max_length=200)
    customer_email = models.EmailField()
    customer_address = models.TextField()
    payment_method = models.CharField(max_length=20, choices=PAYMENT_CHOICES, default='cod')
    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __str__(self):
        return f"Order #{self.id} - {self.customer_name}"
    
    class Meta:
        ordering = ['-created_at']
