from django.contrib import admin

from .models import Ingredient, Tag, Recipe, RecipeIngredient, ShoppingCart


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'color', 'slug',
    )
    search_fields = ('slug',)
    empty_value_display = '-пусто-'


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'text', 'cooking_time',
    )
    inlines = (RecipeIngredientInLine,)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'measurement_unit',
    )
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'user', 'recipe',
    )
    search_fields = ('recipe',)
    empty_value_display = '-пусто-'
