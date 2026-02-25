from rest_framework import serializers
from .models import Product, ProductCategory, Basket


class ProductCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductCategory
        fields = '__all__'


class ProductSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    category = serializers.PrimaryKeyRelatedField(queryset=ProductCategory.objects.all())

    class Meta:
        model = Product
        fields = [
            'id', 'name', 'description', 'price', 'quantity',
            'image', 'category', 'category_name', 'stripe_product_price_id'
        ]
        read_only_fields = ['stripe_product_price_id']


class BasketSerializer(serializers.ModelSerializer):
    product_name = serializers.CharField(source='product.name', read_only=True)
    product_price = serializers.DecimalField(source='product.price', read_only=True, max_digits=10, decimal_places=2)
    total_price = serializers.SerializerMethodField()

    class Meta:
        model = Basket
        fields = [
            'id', 'user', 'product', 'product_name', 'product_price',
            'quantity', 'total_price', 'created_timestamp'
        ]
        read_only_fields = ['user', 'created_timestamp']

    def get_total_price(self, obj):
        return obj.sum()

    def validate_quantity(self, value):
        if value <= 0:
            raise serializers.ValidationError("Количество должно быть больше 0")
        return value

    def validate(self, data):
        product = data.get('product')
        quantity = data.get('quantity')

        if product and quantity and product.quantity < quantity:
            raise serializers.ValidationError(
                f"Доступно только {product.quantity} шт. товара {product.name}"
            )
        return data