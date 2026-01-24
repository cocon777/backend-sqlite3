from django.contrib import admin
from api.models import *
# Register your models here.
admin.site.register(CartItem)
admin.site.register(Category)
admin.site.register(Product)
admin.site.register(Order)
admin.site.register(OrderItem)