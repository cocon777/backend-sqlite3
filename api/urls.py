from django.urls import path
from .views import *
urlpatterns = [
    path('products/',product_list,name='product_list'),
    path('products/<int:pk>/',product_detail,name='product_detail'),
    path('products/filter/',filter_products,name='filter_products'),

    path('categories/',category_list,name='category_list'),
    path('categories/<int:pk>/',category_detail,name='category_detail'),

    path('cart/',cart_list,name='cart_list'),
    path('cart/<int:pk>/',remove_from_cart,name='cart_item_detail'),
    path('cart/item/',get_item_cart_by_product_id,name='get_item_cart_by_product_id'),
    path('cart/item/update/',update_cart_item_quantity,name='update_cart_item_quantity'),

    path('order/create/',create_order,name='create_order'),
    path('order/cancel/<int:order_id>/',cancel_order,name='cancel_order'),
    path('order/',orders_list,name = 'orders_list'),
    
    path('register/',register_user,name='register_user'),
    path('login/',login, name = 'login'),
]