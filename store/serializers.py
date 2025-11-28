from decimal import Decimal

from django.db import transaction

from rest_framework import serializers

from store.models import Product, ReviewProduct, Cart, CartItem, Order, OrderItem, ProductImage


class ProductImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = ProductImage
        fields = ['id', 'image']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ProductImage.objects.create(product_id=product_id, **validated_data)


class ProductSerializer(serializers.ModelSerializer):
    product_images = ProductImageSerializer(many=True, read_only=True)
    class Meta:
        model = Product
        fields = ['id', 'title', 'description', 'price', 'discounted_price', 'product_images']
    discounted_price = serializers.SerializerMethodField(method_name='get_discount')

    def get_discount(self, obj: Product):
        return obj.price - (obj.price * Decimal(0.10))


class ProductReviewSerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewProduct
        fields = ['id', 'name', 'review']

    def create(self, validated_data):
        product_id = self.context['product_id']
        return ReviewProduct.objects.create(
            product_id=product_id,
            **validated_data
        )

class SimpleProductSerializer(serializers.ModelSerializer):
    class Meta:
        model = Product
        fields = ['id', 'title', 'price']

class CartItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    item_total = serializers.SerializerMethodField(method_name='get_item_total')

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity', 'item_total']

    def get_item_total(self, obj):
        return obj.product.price * obj.quantity

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    class Meta:
        model = Cart
        fields = ['cart_id', 'items', 'cart_total']
    cart_total = serializers.SerializerMethodField(method_name='get_cart_total')

    def get_cart_total(self, obj):
        return sum(item.product.price * item.quantity for item in obj.items.all())

class AddCartItemSerializer(serializers.Serializer):
    class Meta:
        model = CartItem
        fields = ['id', 'product', 'quantity']

    def save(self, **kwargs):
        cart_id = self.context['cart_id']
        product_id = self.validated_data['product']
        quantity = self.validated_data['quantity']

        try:
            cart_item = CartItem.objects.get(cart_id=cart_id, product_id=product_id)
            cart_item.quantity = quantity
            cart_item.save()
            self.instance = CartItem.objects.create(cart_id=cart_id)

        except CartItem.DoesNotExist:
            CartItem.objects.create(cart_id=cart_id, **self.validated_data)


        return self.instance

class UpdateCartItemSerializer(serializers.Serializer):
    class Meta:
        model = CartItem
        fields = ['cart_id', 'quantity']

class OrderItemSerializer(serializers.ModelSerializer):
    product = SimpleProductSerializer()
    class Meta:
        model = OrderItem
        fields = ['order', 'product', 'quantity', 'unit_price']

class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    class Meta:
        model = Order
        fields = ['user', 'items']

class CreateOrderSerializer(serializers.Serializer):
    cart_id = serializers.UUIDField()

    def validate_cart_id(self, cart_id):
        if not CartItem.objects.filter(cart_id=cart_id).exists():
            raise serializers.ValidationError('Cart does not exist')
        if CartItem.objects.filter(cart_id=cart_id).count() == 0:
            raise serializers.ValidationError('Cannot place order for empty cart')
        return cart_id

    def save(self, **kwargs):
        with transaction.atomic():
            cart_id = self.validated_data['cart_id']
            user_id = self.context['user_id']

            order = Order.objects.create(user_id=user_id)
            cart_items = CartItem.objects.filter(cart_id=cart_id)

            order_items = [
                OrderItem(
                    order=order,
                    product=item.product,
                    quantity=item.quantity,
                    unit_price=item.product.price
                )
                for item in cart_items
            ]

            OrderItem.objects.bulk_create(order_items)

            Cart.objects.create(cart_id=cart_id).delete()

        return order