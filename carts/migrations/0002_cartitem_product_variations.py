# Generated by Django 5.1.3 on 2024-11-22 12:59

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('carts', '0001_initial'),
        ('store', '0002_productvariation'),
    ]

    operations = [
        migrations.AddField(
            model_name='cartitem',
            name='product_variations',
            field=models.ManyToManyField(blank=True, to='store.productvariation'),
        ),
    ]