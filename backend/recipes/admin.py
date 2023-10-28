from django import forms
from django.contrib import admin
from django.utils.safestring import mark_safe

from .models import (Favorite, FoodUser, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)


@admin.register(FoodUser)
class FoodUserAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'username', 'email', 'first_name', 'last_name',
        'count_recipes', 'count_follower', 'count_following')
    search_fields = ('username',)
    empty_value_display = '-пусто-'

    @admin.display(description='рецепты')
    def count_recipes(self, user):
        return user.recipe.count()

    @admin.display(description='подписки')
    def count_follower(self, user):
        return user.follower.count()

    @admin.display(description='подписчики')
    def count_following(self, user):
        return user.following.count()


@admin.register(Subscription)
class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ('user', 'author',)
    search_fields = ('user',)
    empty_value_display = '-пусто-'


class TagForm(forms.ModelForm):
    color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'color', 'slug',)
    form = TagForm
    search_fields = ('slug',)
    empty_value_display = '-пусто-'


class RecipeIngredientInLine(admin.TabularInline):
    model = RecipeIngredient
    extra = 1
    readonly_fields = ('unit',)

    @admin.display(description='мера')
    def unit(self, recipeingredient):
        return recipeingredient.ingredient.measurement_unit


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id', 'name', 'text', 'cooking_time', 'count_in_favorites',)
    readonly_fields = ('count_in_favorites', 'image_preview', 'tags_all')
    inlines = (RecipeIngredientInLine,)
    search_fields = ('name',)
    empty_value_display = '-пусто-'

    @admin.display(description='в избранных')
    def count_in_favorites(self, recipe):
        return recipe.favorite.count()

    @admin.display(description='изображение')
    def image_preview(self, recipe):
        return mark_safe(
            f'<img src="{recipe.image.url}" style="max-height: 350px;">')

    @admin.display(description='теги')
    def tags_all(self, obj):
        return ', '.join(tag.name for tag in obj.tags.all())


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit',)
    search_fields = ('name',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('recipe',)
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('recipe',)
    empty_value_display = '-пусто-'
