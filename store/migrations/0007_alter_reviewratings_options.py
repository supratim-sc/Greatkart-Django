# Generated by Django 5.1.3 on 2025-01-02 05:09

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('store', '0006_alter_reviewratings_user_profile'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='reviewratings',
            options={'verbose_name': 'Review Rating', 'verbose_name_plural': 'Review Ratings'},
        ),
    ]
