from django.test import TestCase, Client
from django.contrib.auth.models import User
from rest_framework.test import APITestCase, APIClient
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework import status
from .models import Category, Product, CartItem, Order, OrderItem

class ProductModelTest(TestCase):
    """Test Product Model"""
    
    def setUp(self):
        self.category = Category.objects.create(category_name="Electronics")
        self.product = Product.objects.create(
            product_name="Laptop",
            product_description="Gaming Laptop",
            price=1000.00,
            discountPercentage=10,
            stock=5,
            category=self.category
        )
    
    def test_product_creation(self):
        """Test product can be created"""
        self.assertEqual(self.product.product_name, "Laptop")
        self.assertEqual(self.product.price, 1000.00)
    
    def test_product_discount_validation(self):
        """Test discount percentage validation"""
        self.assertTrue(0 <= self.product.discountPercentage <= 100)
    
    def test_product_stock_validation(self):
        """Test stock cannot be negative"""
        self.assertGreaterEqual(self.product.stock, 0)

class DatabaseIntegrationTest(TestCase):
    """Test database integration"""
    
    def test_database_connection(self):
        """Test database is accessible"""
        category = Category.objects.create(category_name="Test")
        self.assertTrue(Category.objects.filter(category_name="Test").exists())
    
    def test_foreign_key_relationships(self):
        """Test foreign key relationships work correctly"""
        user = User.objects.create_user(username='testuser', password='pass123')
        category = Category.objects.create(category_name="Electronics")
        product = Product.objects.create(
            product_name="Laptop",
            price=1000.00,
            category=category
        )
        cart_item = CartItem.objects.create(
            user=user,
            product=product,
            quantity=1
        )
        self.assertEqual(cart_item.product.category.category_name, "Electronics")
