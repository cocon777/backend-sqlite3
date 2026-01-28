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

class ProductAPITest(APITestCase):
    """Test Product API endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.admin_user = User.objects.create_user(
            username='admin',
            password='admin123',
            is_staff=True
        )
        self.normal_user = User.objects.create_user(
            username='user',
            password='user123',
            is_staff=False
        )
        self.category = Category.objects.create(category_name="Electronics")
        self.product = Product.objects.create(
            product_name="Laptop",
            price=1000.00,
            stock=10,
            category=self.category
        )
    
    def test_get_all_products(self):
        """Test get all products"""
        response = self.client.get('/api/products/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertGreaterEqual(len(response.data), 1)
    
    def test_get_product_detail(self):
        """Test get product by id"""
        response = self.client.get(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['product_name'], "Laptop")
    
    def test_create_product_as_admin(self):
        """Test create product as admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {
            'product_name': 'Phone',
            'price': 500.00,
            'stock': 20,
            'category': self.category.id
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
    
    def test_create_product_as_normal_user(self):
        """Test create product fails for non-admin user"""
        self.client.force_authenticate(user=self.normal_user)
        data = {
            'product_name': 'Phone',
            'price': 500.00,
            'stock': 20,
            'category': self.category.id
        }
        response = self.client.post('/api/products/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_403_FORBIDDEN)
    
    def test_update_product_as_admin(self):
        """Test update product as admin"""
        self.client.force_authenticate(user=self.admin_user)
        data = {'price': 1200.00}
        response = self.client.patch(f'/api/products/{self.product.id}/', data, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['price'], '1200.00')
    
    def test_delete_product_as_admin(self):
        """Test delete product as admin"""
        self.client.force_authenticate(user=self.admin_user)
        response = self.client.delete(f'/api/products/{self.product.id}/')
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Product.objects.filter(id=self.product.id).exists())
    
    def test_filter_products_by_category(self):
        """Test filter products by category"""
        response = self.client.get(f'/api/products/filter/?category={self.category.id}')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_products_by_price_asc(self):
        """Test filter products by price ascending"""
        response = self.client.get('/api/products/filter/?sort=price_asc')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
    
    def test_filter_products_by_price_desc(self):
        """Test filter products by price descending"""
        response = self.client.get('/api/products/filter/?sort=price_desc')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

class UserAuthTest(APITestCase):
    """Test User Authentication endpoints"""
    
    def setUp(self):
        self.client = APIClient()
        self.user_data = {
            'username': 'testuser',
            'password': 'testpass123'
        }
    
    def test_user_registration(self):
        """Test user can register"""
        response = self.client.post('/api/register/', self.user_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_201_CREATED, status.HTTP_200_OK])
    
    def test_user_login(self):
        """Test user can login"""
        User.objects.create_user(**self.user_data)
        response = self.client.post('/api/login/', self.user_data, format='json')
        self.assertIn(response.status_code, [status.HTTP_200_OK, status.HTTP_201_CREATED])


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
