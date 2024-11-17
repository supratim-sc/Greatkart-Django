from django.urls import path

from . import views

urlpatterns = [
    path('', views.store, name='store'),
    
    # adding 'category/' to urls so that we can have 'search/' endpoint seperately 
    # otherwise, we need to tweak for the 'search/' endpoint
    path('category/<slug:category_slug>/', views.store, name='products_by_category'),
    path('category/<slug:category_slug>/<slug:product_slug>/', views.product_details, name='product_details'),

    path('search/', views.search, name='search'),
]