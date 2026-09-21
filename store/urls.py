from django.urls import path
from . import views

app_name = 'store'

urlpatterns = [
    path('login/', views.login_view, name='login'),
    path('register/', views.register_view, name='register'),
    path('logout/', views.logout_view, name='logout'),
    path('', views.home, name='home'),
    path('shop/', views.product_list, name='product_list'),
    path('shop/<slug:category_slug>/', views.product_list, name='product_list_by_category'),
    path('product/<slug:slug>/', views.product_detail, name='product_detail'),

    path('cart/', views.cart_detail, name='cart_detail'),
    path('cart/add/<int:product_id>/', views.cart_add, name='cart_add'),
    path('cart/update/<int:product_id>/', views.cart_update, name='cart_update'),
    path('cart/remove/<int:product_id>/', views.cart_remove, name='cart_remove'),

    path('checkout/', views.checkout, name='checkout'),
    path('order/success/<uuid:order_number>/', views.order_success, name='order_success'),
    path("wishlist/", views.wishlist, name="wishlist",),
    path("wishlist/add/<int:product_id>/", views.add_to_wishlist, name="add_to_wishlist"),
    path("customer-service/", views.customer_service, name="customer_service"),
    path("newsletter/subscribe/", views.newsletter_subscribe, name="newsletter_subscribe"),
    path("wishlist/remove/<int:product_id>/", views.remove_from_wishlist, name="remove_from_wishlist"),
]
