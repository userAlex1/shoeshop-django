"""
Simple session-based shopping cart.
Cart is stored in the Django session as:
{
    "<product_id>__<size>": {"quantity": 2, "size": "42"}
}
"""
from decimal import Decimal
from .models import Product

CART_SESSION_KEY = 'cart'


class Cart:
    def __init__(self, request):
        self.session = request.session
        cart = self.session.get(CART_SESSION_KEY)
        if cart is None:
            cart = self.session[CART_SESSION_KEY] = {}
        self.cart = cart

    def _key(self, product_id, size):
        return f"{product_id}__{size}"

    def add(self, product, size, quantity=1):
        key = self._key(product.id, size)
        if key in self.cart:
            self.cart[key]['quantity'] += quantity
        else:
            self.cart[key] = {'quantity': quantity, 'size': size, 'product_id': product.id}
        self.save()

    def update(self, product_id, size, quantity):
        key = self._key(product_id, size)
        if key in self.cart:
            if quantity <= 0:
                del self.cart[key]
            else:
                self.cart[key]['quantity'] = quantity
            self.save()

    def remove(self, product_id, size):
        key = self._key(product_id, size)
        if key in self.cart:
            del self.cart[key]
            self.save()

    def save(self):
        self.session.modified = True

    def clear(self):
        self.session[CART_SESSION_KEY] = {}
        self.save()

    def __iter__(self):
        product_ids = [item['product_id'] for item in self.cart.values()]
        products = Product.objects.filter(id__in=product_ids)
        products_map = {p.id: p for p in products}
        for key, item in self.cart.items():
            product = products_map.get(item['product_id'])
            if not product:
                continue
            yield {
                'product': product,
                'size': item['size'],
                'quantity': item['quantity'],
                'price': product.price,
                'subtotal': product.price * item['quantity'],
            }

    def __len__(self):
        return sum(item['quantity'] for item in self.cart.values())

    def total_price(self):
        total = Decimal('0')
        for item in self:
            total += item['subtotal']
        return total
