from django.shortcuts import render
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated

from apps.products.models import Product
from .models import Order, Inventory, OrderItem
from apps.users.models import Address, Cart
import uuid
from django.shortcuts import get_object_or_404

from .models import Order  # Assuming Order model exists
from .serializers import OrderSerializer  # Create this if not made yet

# Create your views here.
@api_view(['POST'])
@permission_classes([IsAuthenticated])
def place_order(request):
    user = request.user
    cart_code = request.data.get('cart_code')
    address_id = request.data.get('address_id')

    try:
        cart = Cart.objects.get(cart_code=cart_code)
        cart_items = cart.cartitems.all()

        if not cart_items.exists():
            return Response({'error': 'Cart is empty'}, status=400)

        try:
            address = Address.objects.get(id=address_id, user=user)
        except Address.DoesNotExist:
            return Response({'error': 'Invalid address selected'}, status=400)

        total = sum(item.product.price * item.quantity for item in cart_items)

        order = Order.objects.create(
            user=user,
            address=address,
            order_code=str(uuid.uuid4()),
            total_price=total
        )

        for item in cart_items:
            OrderItem.objects.create(
                order=order,
                product=item.product,
                quantity=item.quantity,
                price=item.product.price
            )

            # Inventory update yaha ho sakta hai

        cart_items.delete()
        return Response({'message': 'Order placed successfully', 'order_code': order.order_code})

    except Cart.DoesNotExist:
        return Response({'error': 'Cart not found'}, status=404)









@api_view(['POST'])
@permission_classes([IsAuthenticated])
def order_now(request):
    user = request.user
    product_id = request.data.get('product_id')
    address_id = request.data.get('address_id')
    quantity = int(request.data.get('quantity', 1))

    try:
        product = Product.objects.get(id=product_id)
        address = Address.objects.get(id=address_id, user=user)
    except (Product.DoesNotExist, Address.DoesNotExist):
        return Response({'error': 'Invalid product or address'}, status=400)

    order = Order.objects.create(user=user, address=address, total=product.price * quantity)
    OrderItem.objects.create(order=order, product=product, quantity=quantity)

    # Reduce inventory if required
    # Inventory.objects.filter(product=product).update(quantity=F('quantity') - quantity)

    return Response({'message': 'Order placed successfully', 'order_id': order.id})




@api_view(['GET'])
@permission_classes([IsAuthenticated])
def my_orders(request):
    user = request.user
    orders = Order.objects.filter(user=user).order_by('-created_at')  # Latest first
    serializer = OrderSerializer(orders, many=True)
    return Response({"orders": serializer.data})
