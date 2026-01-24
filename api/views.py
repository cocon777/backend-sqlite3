from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import *
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .serializer import *
from django.contrib.auth.models import User
from rest_framework_simplejwt.tokens import RefreshToken
# Create your views here.
###product api
@api_view(['GET', 'POST'])
def product_list(request):
    if request.method == 'GET':
        products = Product.objects.all()
        serializer = ProductSerializer(products, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        if not request.user.is_staff:
            return Response({"detail": "Is Admin only."}, status=403)
        
        serializer = ProductSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
###get, patch, delete san pham theo id
@api_view(['GET', 'PATCH', 'DELETE'])
def product_detail(request, pk):
    try:
        product = Product.objects.get(pk=pk)
    except Product.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = ProductSerializer(product)
        return Response(serializer.data)

    elif request.method == 'PATCH':
        if not request.user.is_staff:
            return Response({"detail": "Is Admin only."}, status=403)
        serializer = ProductSerializer(product, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    elif request.method == 'DELETE':
        if not request.user.is_staff:
            return Response({"detail": "Is Admin only."}, status=403)
        product.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
### sap xep asc, desc theo gia, loc theo category
# /products/filter?sort=price_asc
# /products/filter?sort=price_desc
# /products/filter?category=category_id
@api_view(['GET'])
def filter_products(request):
    sort = request.query_params.get('sort')
    category_id = request.query_params.get('category')
    products = Product.objects.all()

    if not sort and not category_id:
        return Response({"detail": "At least one filter parameter (sort or category) is required."}, status=status.HTTP_400_BAD_REQUEST)

    if category_id:
        products = products.filter(category__category_id=category_id)
    if sort == 'price_asc':
        products = products.order_by('price')
    elif sort == 'price_desc':
        products = products.order_by('-price')

    serializer = ProductSerializer(products, many=True)
    return Response(serializer.data)
# categories
###get toan bo danh muc
@api_view(['GET'])
def category_list(request):
    if request.method == 'GET':
        categories = Category.objects.all()
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
###get danh muc theo id
@api_view(['GET'])
def category_detail(request, pk):
    try:
        category = Category.objects.get(pk=pk)
    except Category.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'GET':
        serializer = CategorySerializer(category)
        return Response(serializer.data)
# cart
###view gio hang, them moi san pham vao gio hang
@api_view(['GET', 'POST'])
@permission_classes([IsAuthenticated])
def cart_list(request):
    if request.method == 'GET':
        cart_items = CartItem.objects.filter(user = request.user)
        serializer = CartItemSerializer(cart_items, many=True)
        return Response(serializer.data)

    elif request.method == 'POST':
        serializer = CartItemSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user = request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
###PATCH so luong san pham trong gio hang theo product_id ?product_id=1
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def update_cart_item_quantity(request):
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response({"detail": "product_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        cart_item = CartItem.objects.get(user = request.user,product__product_id=product_id)
    except CartItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = CartItemSerializer(cart_item, data=request.data, partial=True)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
###lay thong tin 1 san pham trong gio hang theo product_id
@api_view(['GET']) 
@permission_classes([IsAuthenticated])
def get_item_cart_by_product_id(request):
    product_id = request.query_params.get('product_id')
    if not product_id:
        return Response({"detail": "product_id query parameter is required."}, status=status.HTTP_400_BAD_REQUEST)
    try:
        cart_item = CartItem.objects.get(user=request.user,product__product_id=product_id) #lấy CartItem mà sản phẩm có product_id = product_id
    except CartItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = CartItemSerializer(cart_item)
    return Response(serializer.data)
### xoa san pham khoi gio hang theo id
@api_view(['DELETE'])
@permission_classes([IsAuthenticated])
def remove_from_cart(request, pk):
    try:
        cart_item = CartItem.objects.get(pk=pk,user=request.user)
    except CartItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    if request.method == 'DELETE':
        cart_item.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

###order:
@api_view(["POST"])
@permission_classes([IsAuthenticated])
def create_order(request):
    user = request.user

    cart_items = request.data.get("cartItems", [])
    address = request.data.get("address", "")
    phone = request.data.get("phone", "")
    note = request.data.get("note", "")

    if not cart_items:
        return Response({"detail": "Your Cart is empty."}, status=400)

    if not address:
        return Response({"detail": "The Address is required."}, status=400)
    if not phone:
        return Response({"detail": "The Phone is required."}, status=400)

    order = Order.objects.create(
        customer=user,
        address=address,
        phone=phone,
        note=note,
        status="processing"
    )

    total = 0  # tong tien

    for item in cart_items:
        product_id = item.get("product_id")
        quantity = item.get("quantity", 1)

        try:
            product = Product.objects.get(product_id=product_id)
        except Product.DoesNotExist:
            return Response({"detail": f"Product {product_id} not found."}, status=400)

        if product.stock < quantity:  # kiem tra ton kho
            return Response(
                {"detail": f"Not enough stock for {product.product_name}."},
                status=400
            )

        OrderItem.objects.create(
            order=order,
            product=product,
            quantity=quantity,
            price=product.price * quantity
        )

        total += product.price * quantity

        product.stock -= quantity
        product.save()

    order.total = total
    order.save()

    CartItem.objects.filter(user=user).delete()

    return Response({
        "order_id": order.id,
        "status": order.status,
        "address": order.address,
        "phone": order.phone,
        "note": order.note,
        "total": float(order.total),
        "time_create": order.time_create,
    }, status=status.HTTP_201_CREATED)
@api_view(['PATCH'])
@permission_classes([IsAuthenticated])
def cancel_order(request, order_id):
    try:
        order = Order.objects.get(id=order_id)
    except Order.DoesNotExist:
        return Response({"detail": "Order not found."}, status=status.HTTP_404_NOT_FOUND)

    if order.customer != request.user:
        return Response({"detail": "You do not have permission to cancel this order."}, status=403)

    if order.status in ['paid', 'shipped']:
        return Response({"detail": f"Cannot cancel an order with status '{order.status}'."}, status=400)

    order.status = 'canceled'
    order.save()

    for item in order.items.all():  # tra lai so luong san pham vao kho
        if item.product:
            item.product.stock += item.quantity
            item.product.save()

    return Response({
        "detail": f"Order {order.id} has been canceled.",
        "status": order.status
    })

#get toan bo order 1 user da tao
@api_view(['GET'])
@permission_classes([IsAuthenticated])
def orders_list(request):
    orders = Order.objects.filter(customer=request.user).order_by('-time_create')
    serializer = OrderSerializer(orders, many=True)
    return Response(serializer.data)

#register
@api_view(['POST'])
@permission_classes([AllowAny])
def register_user(request):
    serializer = RegisterSerializer(data=request.data)
    if serializer.is_valid():
        user = serializer.save()
        return Response(
            {
                'message': 'registered successfully!',
                'user_id': user.id,
            },
            status=status.HTTP_201_CREATED
        )
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

###login
@api_view(['POST'])
def login(request):
    username = request.data.get("username")
    password = request.data.get("password")

    user = authenticate(username=username, password=password)
    if user is None:
        return Response({"detail": "Invalid username or password"}, status=status.HTTP_401_UNAUTHORIZED)

    refresh = RefreshToken.for_user(user)

    return Response({
        "message": "Login successful!",
        "user_id": user.id,
        "role": "admin" if user.is_staff else "user",
        "refresh": str(refresh),
        "access": str(refresh.access_token)
    }, status=status.HTTP_200_OK)