from ast import literal_eval

from django import forms
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from django.contrib.auth.models import Group
from django.utils.safestring import mark_safe
from django.utils.translation import gettext_lazy as _

from .models import (Favorite, FoodUser, Ingredient, Recipe, RecipeIngredient,
                     ShoppingCart, Subscription, Tag)

admin.site.unregister(Group)


@admin.register(FoodUser)
class FoodUserAdmin(UserAdmin):
    list_display = (
        'id',
        'username',
        'email',
        'first_name',
        'last_name',
        'count_recipes',
        'count_follower',
        'count_following')
    search_fields = ('username',)

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


class TagForm(forms.ModelForm):
    color = forms.CharField(
        widget=forms.TextInput(attrs={'type': 'color'}))

    class Meta:
        model = Tag
        fields = ('name', 'color', 'slug',)


@admin.register(Tag)
class TagAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'tag_color', 'slug',)
    form = TagForm
    search_fields = ('slug',)

    @admin.display(description='цвет')
    def tag_color(self, tag):
        return mark_safe(f'<span style="color:{tag.color};">{"|"*10}</span>')


class RecipeIngredientInLine(admin.StackedInline):
    model = RecipeIngredient
    extra = 1
    min_num = 1


class CookingSpeedFilter(admin.SimpleListFilter):
    title = _('Время приготовления')
    parameter_name = 'speed'

    def lookups(self, request, model_admin):
        if not (
            times := sorted(model_admin.get_queryset(
                request).values_list('cooking_time', flat=True))):
            return
        threshold_1 = times[int(len(times) / 3)]
        threshold_2 = times[int(len(times) * 2 / 3)]
        fast = (0, threshold_1)
        medium = (threshold_1, threshold_2)
        slow = (threshold_2, times[-1])
        return (
            (fast, _(f'Быстро: {fast[0]} - {fast[1]} минут')),
            (medium, _(f'Средне: {medium[0]} - {medium[1]} минут')),
            (slow, _(f'Медленно: {slow[0]} - {slow[1]} минут')))

    def queryset(self, request, queryset):
        if not self.value():
            return queryset
        start, end = literal_eval(self.value())
        return queryset.filter(cooking_time__range=(start, end))


@admin.register(Recipe)
class RecipeAdmin(admin.ModelAdmin):
    list_display = (
        'id',
        'name',
        'text',
        'cooking_time',
        'image_preview_small',
        'count_in_favorites',
        'ingredients_all',
        'tags_all')
    readonly_fields = (
        'count_in_favorites',
        'image_preview_big',
        'tags_all',
        'ingredients_all')
    search_fields = ('name',)
    empty_value_display = ''
    inlines = (RecipeIngredientInLine,)
    list_filter = (
        CookingSpeedFilter,
        ('tags', admin.RelatedOnlyFieldListFilter))

    @admin.display(description='в избранных')
    def count_in_favorites(self, recipe):
        return recipe.favorites.count()

    @admin.display(description='изображение')
    def image_preview_big(self, recipe):
        return mark_safe(
            f'<img src="{recipe.image.url}" style="max-height: 350px;">')

    @admin.display(description='изображение')
    def image_preview_small(self, recipe):
        return mark_safe(
            f'<img src="{recipe.image.url}" style="max-height: 100px;">')

    @admin.display(description='теги')
    def tags_all(self, recipe):
        return mark_safe('<br>'.join(tag.name for tag in recipe.tags.all()))

    @admin.display(description='продукты')
    def ingredients_all(self, recipe):
        return mark_safe('<br>'.join(
            ingredient.name for ingredient in recipe.ingredients.all()))


@admin.register(Ingredient)
class IngredientAdmin(admin.ModelAdmin):
    list_display = ('id', 'name', 'measurement_unit', 'count_in_recipes',)
    search_fields = ('name',)
    list_filter = ('measurement_unit',)

    @admin.display(description='в рецептах')
    def count_in_recipes(self, ingredient):
        return ingredient.recipe_ingredient.count()


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('recipe',)


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'recipe',)
    search_fields = ('recipe',)
