from django.db import models
from django.urls import reverse

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        # Changing plural name from 'Categorys' to 'Categories'
        verbose_name_plural = 'Categories'

    # creating custom method to get the url based on the slug
    def get_url(self):
        '''The reverse() resolves the URL as soon as it is called. 
        This means that the view name and any arguments you pass to it are immediately converted into a URL string.'''
        # creating the URL with the URL 'name' and passing slug as argument to it
        return reverse('products_by_category', args=[self.slug])

    def __str__(self) -> str:
        return self.name