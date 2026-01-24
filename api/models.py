from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator
from django.contrib.auth.models import User

# Create your models here.
class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    category_name = models.CharField(max_length=100)

    def __str__(self):
        return self.category_name

class Product(models.Model):
    product_id = models.AutoField(primary_key=True)
    product_name = models.CharField(max_length=200)
    product_description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discountPercentage = models.DecimalField(
        max_digits=5, 
        decimal_places=2, 
        blank=True, 
        null=True,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    stock = models.IntegerField(blank=True, null=True, validators=[MinValueValidator(0)])
    image_url = models.CharField(max_length=255, blank=True, null=True)
    category = models.ForeignKey(Category, models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.product_name

class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)  # Thêm cột user_id
    product = models.ForeignKey(Product, models.CASCADE, blank=False, null=False)
    quantity = models.IntegerField(validators=[MinValueValidator(1)])

    def __str__(self):
        return f"{self.product.product_name} x {self.quantity} ({self.user.username})"

class Order(models.Model):
    customer = models.ForeignKey(User, on_delete=models.SET_NULL, null=True)
    address = models.CharField(max_length=255)
    phone = models.CharField(max_length=20,default='0000000000') 
    note = models.TextField(blank=True, null=True)
    time_create = models.DateTimeField(auto_now_add=True)
    total = models.DecimalField(max_digits=10, decimal_places=2, default=0)
    status = models.CharField(
        max_length=20,
        choices=[
            ('pending','Pending'),
            ('processing','Processing'),
            ('paid','Paid'),
            ('shipped','Shipped'),
            ('canceled','Canceled')
        ],
        default='pending'
    )

    def __str__(self):
        return f"Order {self.id} by {self.customer or 'Deleted user'}"

class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    quantity = models.IntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        product_name = self.product.product_name if self.product else "Deleted Product"
        return f"{product_name} x {self.quantity}"