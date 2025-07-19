from django.contrib import admin
from django.urls import path,include
from .views import (
    home, mylogin, mysignup, activate, productdetail,
    mylogout, add_to_cart, view_cart,
    increase_quantity, decrease_quantity, remove_from_cart,process_checkout,order_confirmation)

from .api_views import (
    ProductViewSet, CategoryViewSet, CartViewSet, OrderViewSet, OrderItemViewSet
)


from rest_framework_simplejwt.views import (
    TokenObtainPairView,
    TokenRefreshView,
)

from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register('products', ProductViewSet)
router.register('categories', CategoryViewSet)
router.register('cart', CartViewSet)
router.register('orders', OrderViewSet)
router.register('order-items', OrderItemViewSet)

urlpatterns = [
    path('', home, name='home'),
    path('api/', include(router.urls)),
    path('login/', mylogin, name='login'),
    path('logout/', mylogout, name='logout'),
    path('signup/', mysignup, name='signup'),
    path('add-to-cart/', add_to_cart, name='add_to_cart'),
    path('cart/', view_cart, name='view_cart'),
    path('cart/increase/', increase_quantity, name='increase_quantity'),   # ✅ Increase
    path('cart/decrease/', decrease_quantity, name='decrease_quantity'),   # ✅ Decrease
    path('cart/remove/', remove_from_cart, name='remove_from_cart'),       # ✅ Remove
    path('process_checkout/', process_checkout, name='process_checkout'),
    path('order_confirmation/<int:order_id>/', order_confirmation, name='order_confirmation'),
    path('activate/<str:id>/', activate, name='activate'),
    path('product-detail/<int:pk>', productdetail, name='product-detail'),
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),  # Login
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),  # Refresh

]
