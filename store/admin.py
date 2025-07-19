from django.contrib import admin

# Register your models here.
from.models.product import Product
from.models.category import Category
from.models.cart import Cart
from.models.order import Order
from.models.orderitem import OrderItem
class Adminproduct(admin.ModelAdmin):
   list_display= ['id','name','price','category','description']



admin.site.register(Product, Adminproduct)
admin.site.register(Category)
admin.site.register(Cart)
admin.site.register(Order)
admin.site.register(OrderItem)


