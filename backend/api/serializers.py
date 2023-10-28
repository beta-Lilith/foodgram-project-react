from collections import Counter

from djoser.serializers import UserCreateSerializer, UserSerializer
from drf_extra_fields.fields import Base64ImageField
from django.shortcuts import get_object_or_404
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator

from recipes.models import FoodUser, Ingredient, Recipe, RecipeIngredient, Tag

NO_INGREDIENTS = 'Добавьте ингридиенты'
NO_INGREDIENTS_DB = 'Этого ингредиента нет в базе'

NO_TAGS = 'Добавьте теги'

CHECK_UNIQUE = 'Объекты должны быть уникальными. Повторяются: {}'

NO_IMAGE = 'Добавьте картинку'

RECIPE_NO_INGREDIENTS = 'Ингредиенты обязательны для рецепта'
RECIPE_NO_TAGS = 'Нужен хотя бы один тег'

NOT_INT = 'Введите число >= 0, вы ввели: {}'


def check_is_anonymous(func):
    def wrapper(self, obj):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return func(self, obj)
    return wrapper


class FoodUserSerializer(UserSerializer):
    is_subscribed = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = FoodUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',)

    @check_is_anonymous
    def get_is_subscribed(self, user):
        return user.following.filter(
            user=self.context.get('request').user
        ).exists()


class FoodUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=(UniqueValidator(queryset=FoodUser.objects.all()),))

    class Meta:
        model = FoodUser
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',)


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug',)


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id')
    name = serializers.ReadOnlyField(
        source='ingredient.name')
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit')

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount',)


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    author = UserSerializer(read_only=True)
    ingredients = RecipeIngredientSerializer(
        many=True, source='recipe_ingredient')
    is_favorited = serializers.SerializerMethodField(read_only=True)
    is_in_shopping_cart = serializers.SerializerMethodField(read_only=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'is_favorited',
            'is_in_shopping_cart',
            'name',
            'image',
            'text',
            'cooking_time',)

    @check_is_anonymous
    def get_is_favorited(self, recipe):
        return self.context.get(
            'request').user.favorites.filter(recipe=recipe).exists()

    @check_is_anonymous
    def get_is_in_shopping_cart(self, recipe):
        return self.context.get(
            'request').user.shoppingcarts.filter(recipe=recipe).exists()


class AddIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True,)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'name',
            'image',
            'text',
            'cooking_time',)

    def check_unique(self, obj_list):
        if len(obj_list) != len(set(obj_list)):
            not_unique = [
                obj.name
                for obj, count in Counter(obj_list).items()
                if count > 1]
            raise ValidationError(
                CHECK_UNIQUE.format(not_unique))

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(NO_INGREDIENTS)
        self.check_unique([
            get_object_or_404(Ingredient, id=ingredient['id'])
            for ingredient in value])
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError(NO_TAGS)
        self.check_unique(value)
        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError(NO_IMAGE)
        return value

    def set_ingredients(self, recipe, ingredients):
        RecipeIngredient.objects.bulk_create(
            RecipeIngredient(
                recipe=recipe,
                ingredient_id=data['id'],
                amount=data['amount'])
            for data in ingredients)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.set_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        if not validated_data.get('ingredients'):
            raise ValidationError(RECIPE_NO_INGREDIENTS)
        ingredients = validated_data.pop('ingredients')
        if not validated_data.get('tags'):
            raise ValidationError(RECIPE_NO_TAGS)
        tags = validated_data.pop('tags')
        recipe = super().update(recipe, validated_data)
        recipe.tags.clear()
        recipe.ingredients.clear()
        self.set_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        recipe.save()
        return recipe

    def to_representation(self, recipe):
        return RecipeSerializer(
            recipe,
            context={'request': self.context.get('request')}
        ).data


class RecipeCutFieldsSerializer(serializers.ModelSerializer):
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time',)


class SubscriptionSerializer(FoodUserSerializer):
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(FoodUserSerializer.Meta):
        fields = FoodUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',)
        read_only_fields = ('username',)
        extra_kwargs = {
            'email': {'required': False},
            'first_name': {'required': False},
            'last_name': {'required': False}}

    def get_recipes_count(self, author):
        return author.recipe.count()

    def get_recipes(self, obj):
        limit = self.context.get('request').GET.get('recipes_limit', 10**10)
        try:
            recipes = obj.recipe.all()[:int(limit)]
        except ValueError:
            raise ValidationError(NOT_INT.format(limit))
        return RecipeCutFieldsSerializer(
            recipes, many=True, read_only=True).data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
