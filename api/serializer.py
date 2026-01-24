from rest_framework import serializers
from .models import *
from django.contrib.auth.models import User
from django.contrib.auth import authenticate

class CategorySerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='category_id', read_only=True)
    name = serializers.CharField(source='category_name')
    class Meta:
        model = Category
        fields = ['id', 'name']

class ProductSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='product_id', read_only=True)
    price = serializers.DecimalField(max_digits=10, decimal_places=2, coerce_to_string=False)
    title = serializers.CharField(source='product_name')
    description = serializers.CharField(source='product_description')
    categoryId = serializers.PrimaryKeyRelatedField(queryset=Category.objects.all(), source='category')
    discountPercentage = serializers.DecimalField(max_digits=5, decimal_places=2, coerce_to_string=False)
    thumbnail = serializers.CharField(source='image_url')
    class Meta:
        model = Product
        fields = ['id', 'title', 'description','categoryId', 'price', 'discountPercentage', 'stock', 'thumbnail']
class CartItemSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(source='cart_item_id', read_only=True)
    product_id = serializers.PrimaryKeyRelatedField(queryset=Product.objects.all(), source='product')
    class Meta:
        model = CartItem
        fields = ['product_id', 'quantity', 'id']

class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['product', 'quantity', 'price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'customer', 'address', 'phone',  'note','time_create', 'total' ,'status', 'items']

class RegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, required=True)
    password2 = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ['username', 'password', 'password2','email', 'first_name', 'last_name']
    def validate(self, data):
        if data['password'] != data['password2']: 
            raise serializers.ValidationError("Passwords do not match.")
        if User.objects.filter(email=data['email']).exists():
            raise serializers.ValidationError("Email already registered.")
        return data
    
    def create(self, validated_data):
        validated_data.pop('password2')
        password = validated_data.pop('password')

        user = User(**validated_data)
        user.set_password(password)  # Hash mật khẩu do django
        user.save()
        return user