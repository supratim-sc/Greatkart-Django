from django.shortcuts import render, get_object_or_404, redirect
from django.core.paginator import EmptyPage, PageNotAnInteger, Paginator
from django.db.models import Q
from django.contrib import messages

from .models import Product, ReviewRatings, ProductGallery
from .forms import ReviewRatingsForm

from category.models import Category
from carts.models import Cart, CartItem
from carts.views import _get_cart_id
from orders.models import OrderProduct

# Create your views here.
def store(request, category_slug=None):
    if category_slug:
        category = get_object_or_404(Category, slug=category_slug)
        products = Product.objects.filter(category=category, is_available=True)
    else:
        products = Product.objects.filter(is_available=True).order_by('id')
        
    # --- PAGINATION CONFIGURATION ---
    # creating object of paginator class
    paginator = Paginator(products, 3) # here 3 is the number of products per page

    # getting the page number from the url like "/?page="
    ''' here request.GET.get() is used as for first page we don't have '/?page=' 
    so, if used requset.GET['page] will show error, hence request.GET.get('page)'''
    page = request.GET.get('page')  

    # configuring products per page based on paginator configuration
    paged_products = paginator.get_page(page)
    
    products_count = products.count()
    context = {
        # 'products' : products,
        'products' : paged_products,     # instead of sending all products, sending paged_products only
        'products_count' : products_count,
    }

    return render(request, 'store/store.html', context)

def product_details(request, category_slug, product_slug):
    try:
        product = Product.objects.get(category__slug=category_slug, slug=product_slug)
        # checking if the product is in the cart or not
        # as Cart is the foreignkry to the CartItem model, so we can access cart_id with __ (reverse relationship)
        is_cart_item = CartItem.objects.filter(cart__cart_id=_get_cart_id(request), product=product).exists()
    except Exception as e:
        raise e
    

    # Checking if the current user purchased the product or not
    try:
        is_product_ordered = OrderProduct.objects.filter(user_id=request.user.id, product_id=product.id).exists()

    # if product is not ordered by the current user then set to None
    except OrderProduct.DoesNotExist:
        is_product_ordered = None

    
    # Fetching all the reviews for particular product
    try:
        reviews = ReviewRatings.objects.filter(product_id = product.id, status = True).select_related('user_profile').order_by('-updated_at')

    # if any review for this product does not exists
    except ReviewRatings.DoesNotExist:
        reviews = None

    product_gallery = ProductGallery.objects.filter(product=product)
    
    context = {
        'product' : product,
        'is_cart_item' : is_cart_item,
        'is_product_ordered' : is_product_ordered,  # sending the product ordered by current user status True/None
        'reviews': reviews, # sending all the reviews for this product
        'product_gallery' : product_gallery,    # sending the product gallery
    }
    return render(request, 'store/product_details.html', context)


def search(request):
    products_count = 0
    products = None
    
    if 'keyword' in request.GET:
        keyword = request.GET['keyword']
        products = Product.objects.filter(Q(name__icontains=keyword) | Q(description__icontains=keyword))
        products_count = products.count()

    context = {
        'products' : products,
        'products_count' : products_count,
    }
    return render(request, 'store/store.html', context)


def submit_review(request, product_id):
    # Getting the URL of the current page
    url = request.META.get('HTTP_REFERER')

    # Checking for the POST request
    if request.method == 'POST':
        try:
            # Checking if a rating for the user already exists, then modify/update it
            review = ReviewRatings.objects.get(user_id=request.user.id, product_id=product_id)

            # As we want to update the review, hence passing the instance of the early review
            form = ReviewRatingsForm(request.POST, instance=review)

            # Saving the updated review
            if form.is_valid():
                form.save()

                # Displaying the success message
                messages.success(request, 'Thank you! Your review has been updated.')

                # Redirecting the user to the current page
                return redirect(url)
            else:
                # If the form is not valid, render the form again with errors
                messages.error(request, 'There was an error with your review. Please try again.')
                return redirect(url)

        except ReviewRatings.DoesNotExist:
            # Form for creating a new review if the user hasn't already reviewed this product
            form = ReviewRatingsForm(request.POST)

            print(form.is_valid())

            if form.is_valid():
                # Creating an instance of ReviewRatings model
                data = ReviewRatings()

                data.subject = form.cleaned_data['subject']
                data.review = form.cleaned_data['review']
                data.ratings = form.cleaned_data['ratings']
                data.ip = request.META.get('REMOTE_ADDR')
                data.product_id = product_id
                data.user_id = request.user.id

                # Saving the review
                data.save()

                # Displaying the success message
                messages.success(request, 'Thank You! Your review has been submitted.')

                # Redirecting the user to the current page
                return redirect(url)
            else:
                # If the form is not valid, render the form again with errors
                messages.error(request, 'There was an error with your review. Please try again.')
                return redirect(url)

    # Handle the case where the request is not POST
    return redirect(url)