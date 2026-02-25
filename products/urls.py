from django.urls import path, include
from rest_framework.routers import DefaultRouter

from . import views
from .viewsets import ProductCategoryViewSet, ProductViewSet, BasketViewSet

router = DefaultRouter()
router.register(r'categories', ProductCategoryViewSet)
router.register(r'products', ProductViewSet)
router.register(r'basket', BasketViewSet, basename='basket')

app_name = 'products'
urlpatterns = [
    path('', views.IndexView.as_view(), name='index'),
    path('products/', views.ProductsListView.as_view(), name='products'),
    path('products/category/<int:category_id>', views.ProductsListView.as_view(), name='category'),
    path('products/page/<int:page>', views.ProductsListView.as_view(), name='paginator'),

    path('baskets/add/<int:product_id>', views.basket_add, name='basket_add'),
    path('baskets/remove/<int:basket_id>', views.basket_remove, name='basket_remove'),

    path('api/', include(router.urls)),
]
