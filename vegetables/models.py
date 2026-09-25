from django.db import models
from datetime import datetime
from django.utils import timezone


class useracc(models.Model):
    name = models.CharField(max_length=100,unique=True)
    age = models.IntegerField()
    place = models.CharField(max_length=100)
    phone = models.IntegerField()
    email = models.EmailField()
    password = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class vegetables(models.Model):
    name = models.CharField(max_length=40)
    price = models.IntegerField()
    image = models.ImageField()
    def __str__(self):
        return self.name

class Cart(models.Model):
    user = models.ForeignKey(useracc,on_delete=models.CASCADE)
    product = models.ForeignKey(vegetables, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=0)

class Delivery(models.Model):
    name = models.CharField(max_length=40)
    age = models.IntegerField()
    place = models.CharField(max_length=100)
    phone = models.IntegerField()
    email = models.EmailField()
    password = models.CharField(max_length=30)
    def __str__(self):
        return self.name

class Payment(models.Model):
    user = models.ForeignKey(useracc, on_delete=models.CASCADE, null=True, blank=True)
    name = models.CharField(max_length=40)
    address = models.TextField()
    email = models.EmailField()
    payment = models.CharField(max_length=100)
    totalprice = models.IntegerField()
    date = models.DateTimeField(auto_now_add=True)
    deliver = models.ForeignKey(Delivery, on_delete=models.SET_NULL, null=True, blank=True)
    STATUS_CHOICES = [
        ('Pending', 'Pending'),
        ('Out for Delivery', 'Out for Delivery'),
        ('Delivered', 'Delivered'),
        ('Cancelled', 'Cancelled'),
    ]
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='Pending')
    def __str__(self):
        return f"{self.name} : {self.status}"

class PaidItem(models.Model):
    payment = models.ForeignKey(Payment, on_delete=models.CASCADE,related_name='items')
    product = models.ForeignKey(vegetables,on_delete=models.SET_NULL, null=True)
    quantity = models.PositiveIntegerField(default=1)
    product_name = models.CharField(max_length=200)
    product_price = models.DecimalField(max_digits=10, decimal_places=2)
    product_image = models.ImageField(upload_to='order_items/', null=True, blank=True)

class feedback(models.Model):
    user = models.ForeignKey(useracc, on_delete=models.CASCADE)
    message = models.TextField()
    date = models.DateTimeField(auto_now_add=True)
    def __str__(self):
        return f"{self.user}: {self.message}"

class admins(models.Model):
    name = models.CharField(max_length=40,unique=True)
    password = models.CharField(max_length=30)


    
