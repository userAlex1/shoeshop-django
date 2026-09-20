from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.contrib.auth.decorators import login_required
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.models import User
from .models import Product, Wishlist
from .models import Product, Category, Order, OrderItem
from .cart import Cart


def home(request):
    products = Product.objects.filter(is_active=True)[:12]
    categories = Category.objects.all()
    return render(request, 'store/home.html', {
        'products': products,
        'categories': categories,
    })
def customer_service(request):
    return render(request, "store/customer_service.html")

def product_list(request, category_slug=None):
    category = None
    products = Product.objects.filter(is_active=True)
    categories = Category.objects.all()
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = products.filter(category=category)
    return render(request, 'store/product_list.html', {
        'category': category,
        'categories': categories,
        'products': products,
    })


def product_detail(request, slug):
    product = get_object_or_404(Product, slug=slug, is_active=True)
    return render(request, 'store/product_detail.html', {'product': product})


@require_POST
def cart_add(request, product_id):
    product = get_object_or_404(Product, id=product_id)
    cart = Cart(request)
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))
    cart.add(product=product, size=size, quantity=quantity)
    messages.success(request, f"Added {product.name} (size {size}) to cart.")
    return redirect('store:cart_detail')


def cart_detail(request):
    cart = Cart(request)
    return render(request, 'store/cart.html', {'cart': cart})


@require_POST
def cart_update(request, product_id):
    cart = Cart(request)
    size = request.POST.get('size')
    quantity = int(request.POST.get('quantity', 1))
    cart.update(product_id=product_id, size=size, quantity=quantity)
    return redirect('store:cart_detail')


@require_POST
def cart_remove(request, product_id):
    cart = Cart(request)
    size = request.POST.get('size')
    cart.remove(product_id=product_id, size=size)
    return redirect('store:cart_detail')


def checkout(request):
    cart = Cart(request)
    if len(cart) == 0:
        messages.warning(request, "Your cart is empty.")
        return redirect('store:home')

    if request.method == 'POST':
        full_name = request.POST.get('full_name')
        email = request.POST.get('email', '')
        phone = request.POST.get('phone')
        address = request.POST.get('address')
        city = request.POST.get('city')
        payment_method = request.POST.get('payment_method')

        order = Order.objects.create(
            full_name=full_name,
            email=email,
            phone=phone,
            address=address,
            city=city,
            payment_method=payment_method,
            total_amount=cart.total_price(),
        )
        for item in cart:
            OrderItem.objects.create(
                order=order,
                product=item['product'],
                product_name=item['product'].name,
                size=item['size'],
                quantity=item['quantity'],
                price=item['price'],
            )

        # Route to the right payment flow
        if payment_method == Order.PAYMENT_MPESA:
            return redirect('payments:mpesa_pay', order_number=order.order_number)
        else:
            return redirect('payments:paystack_pay', order_number=order.order_number)

    return render(request, 'store/checkout.html', {'cart': cart})


def order_success(request, order_number):
    order = get_object_or_404(Order, order_number=order_number)
    return render(request, 'store/order_success.html', {'order': order})


def wishlist(request):

    items = Wishlist.objects.filter(
        user=request.user
    ).select_related("product")

    return render(
        request,
        "store/wishlist.html",
        {
            "items": items,
        },
    )

@login_required
def add_to_wishlist(request, product_id):

    product = get_object_or_404(
        Product,
        id=product_id,
    )

    Wishlist.objects.get_or_create(
        user=request.user,
        product=product,
    )

    return redirect(request.META.get("HTTP_REFERER", "store:home"))


@login_required
def remove_from_wishlist(request, product_id):

    Wishlist.objects.filter(
        user=request.user,
        product_id=product_id,
    ).delete()

    return redirect("store:wishlist")

def register_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        email = request.POST.get('email')
        password = request.POST.get('password')
        confirm_password = request.POST.get('confirm_password')

        if password != confirm_password:
            messages.error(request, 'Passwords do not match.')
            return redirect('store:register')

        if User.objects.filter(username=username).exists():
            messages.error(request, 'Username already exists.')
            return redirect('store:register')

        if User.objects.filter(email=email).exists():
            messages.error(request, 'Email already exists.')
            return redirect('store:register')

        user = User.objects.create_user(
            username=username,
            email=email,
            password=password
        )

        messages.success(request, 'Account created successfully. Please log in.')
        return redirect('store:login')

    return render(request, 'store/register.html')


def login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(
            request,
            username=username,
            password=password
        )

        if user is not None:
            login(request, user)
            return redirect('store:home')

        messages.error(request, 'Invalid username or password.')

    return render(request, 'store/login.html')


def logout_view(request):
    logout(request)
    return redirect('store:login')