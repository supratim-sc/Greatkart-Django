from .models import Category

def menu_links(request):
    category_names = Category.objects.all()

    # creating a dictionary with the categories and return if
    return dict(categories=category_names)