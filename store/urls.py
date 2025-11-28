from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import ProductViewSet
from rest_framework_nested import routers
from . import views

router = routers.DefaultRouter()

router.register('products', views.ProductViewSet, basename='products')
router.register('carts', views.CartViewSet, basename='carts')
router.register('orders', views.OrderViewSet, basename='orders')

product_router = routers.NestedDefaultRouter(router, 'products', lookup='product')
product_router.register("reviews", views.ReviewViewSet, basename='reviews')
product_router.register('images', views.ProductImageViewSet, basename='product_images')

cart_router = routers.NestedDefaultRouter(router, "carts", lookup='cart')
cart_router.register('items', views.CartViewSet, basename='carts')

urlpatterns = router.urls + product_router.urls + cart_router.urls
# urlpatterns = [
#     path('', include(router.urls)),
#     path('', include(product_router.urls)),
#     # path('<int:pk>/', views.product_detail, name='product-detail')
# ]