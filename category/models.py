from django.db import models

# Create your models here.
class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField()
    image = models.ImageField(upload_to='photos/categories', blank=True)

    class Meta:
        # Changing plural name from 'Categorys' to 'Categories'
        verbose_name_plural = 'Categories'

    def __str__(self) -> str:
        return self.name