# Generated by Django 3.2 on 2023-10-28 16:07

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipes', '0001_initial'),
    ]

    operations = [
        migrations.RemoveConstraint(
            model_name='favorite',
            name='unique_favorite',
        ),
        migrations.RemoveConstraint(
            model_name='shoppingcart',
            name='unique_shopping_cart',
        ),
    ]