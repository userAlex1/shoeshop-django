import uuid
from django.db import models
from django.urls import reverse
from django.contrib.auth.models import User


class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)

    class Meta:
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def __str__(self):
        return self.name


class Product(models.Model):
    SIZE_CHOICES = [(str(s), str(s)) for s in range(36, 47)]

    category = models.ForeignKey(Category, related_name='products', on_delete=models.SET_NULL, null=True)
    name = models.CharField(max_length=200)
    slug = models.SlugField(unique=True)
    brand = models.CharField(max_length=100, blank=True)
    description = models.TextField(blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, help_text="Price in KES")
    image = models.ImageField(upload_to='products/', blank=True, null=True)
    available_sizes = models.CharField(
        max_length=100, default='38,39,40,41,42,43,44',
        help_text="Comma separated sizes, e.g. 38,39,40"
    )
    stock = models.PositiveIntegerField(default=10)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.name

    def get_absolute_url(self):
        return reverse('store:product_detail', args=[self.slug])

    def sizes_list(self):
        return [s.strip() for s in self.available_sizes.split(',') if s.strip()]


class Order(models.Model):
    STATUS_PENDING = 'pending'
    STATUS_PAID = 'paid'
    STATUS_FAILED = 'failed'
    STATUS_SHIPPED = 'shipped'
    STATUS_CHOICES = [
        (STATUS_PENDING, 'Pending Payment'),
        (STATUS_PAID, 'Paid'),
        (STATUS_FAILED, 'Failed'),
        (STATUS_SHIPPED, 'Shipped'),
    ]

    PAYMENT_MPESA = 'mpesa'
    PAYMENT_CARD = 'card'
    PAYMENT_CHOICES = [
        (PAYMENT_MPESA, 'M-Pesa'),
        (PAYMENT_CARD, 'Card / Bank (Paystack)'),
    ]

    order_number = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    full_name = models.CharField(max_length=200)
    email = models.EmailField(blank=True)
    phone = models.CharField(max_length=20, help_text="Format: 2547XXXXXXXX")
    address = models.CharField(max_length=255)
    city = models.CharField(max_length=100)

    payment_method = models.CharField(max_length=10, choices=PAYMENT_CHOICES, default=PAYMENT_MPESA)
    status = models.CharField(max_length=10, choices=STATUS_CHOICES, default=STATUS_PENDING)

    total_amount = models.DecimalField(max_digits=10, decimal_places=2)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Order {self.order_number} ({self.status})"

    def mark_paid(self):
        self.status = self.STATUS_PAID
        self.save(update_fields=['status', 'updated_at'])


class OrderItem(models.Model):
    order = models.ForeignKey(Order, related_name='items', on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.SET_NULL, null=True)
    product_name = models.CharField(max_length=200)  # snapshot in case product changes/deleted
    size = models.CharField(max_length=10)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def subtotal(self):
        return self.price * self.quantity

    def __str__(self):
        return f"{self.product_name} (size {self.size}) x{self.quantity}"


class Wishlist(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name="wishlist_items"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name="wishlisted_by"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("user", "product")

    def __str__(self):
        return f"{self.user.username} - {self.product.name}"

class NewsletterSubscriber(models.Model):
    email = models.EmailField(unique=True)
    subscribed_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.email