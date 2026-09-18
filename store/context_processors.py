from .cart import Cart
from .models import Category, Wishlist


def cart_summary(request):

    cart = Cart(request)

    wishlist_count = 0

    if request.user.is_authenticated:
        wishlist_count = Wishlist.objects.filter(
            user=request.user
        ).count()

    return {
        "cart_item_count": len(cart),
        "categories": Category.objects.all(),
        "wishlist_count": wishlist_count,
    }