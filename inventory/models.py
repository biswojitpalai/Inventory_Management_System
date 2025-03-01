from django.db import models
from django.contrib.auth.models import User
# Create your models here.

class InventoryItem(models.Model):
    name=models.CharField(max_length=100)
    quantity=models.IntegerField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category=models.ForeignKey('Category',on_delete=models.SET_NULL,blank=True,null=True)
    date_created=models.DateTimeField(auto_now_add=True)
    user=models.ForeignKey(User,on_delete=models.CASCADE)

    def __str__(self):
        return self.name
    

class Category(models.Model):
    name=models.CharField(max_length=200)
    def __str__(self):
        return self.name

    def total_price(self):
        return self.item.price * self.quantity

class Order(models.Model):
    transaction_id = models.CharField(max_length=100, unique=True)
    payment = models.DecimalField(max_digits=10, decimal_places=2)
    products = models.TextField()  # Store product details as text or JSON
    username = models.CharField(max_length=150)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order {self.transaction_id} - {self.username}"
