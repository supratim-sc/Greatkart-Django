from django.urls import path
from . import views

urlpatterns = [
    path('', views.cart, name='cart'),
    path('add_to_cart/<int:product_id>/', views.add_to_cart, name='add_to_cart'),
    path('decrement_item_count/<int:product_id>/', views.decrement_item_count, name='decrement_item_count'),
]