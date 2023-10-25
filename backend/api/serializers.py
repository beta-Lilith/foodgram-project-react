from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserSerializer, UserCreateSerializer
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import User
from drf_extra_fields.fields import Base64ImageField
from django.core.exceptions import ObjectDoesNotExist


NO_INGREDIENTS = 'Добавьте ингридиенты'
NO_INGREDIENTS_DB = 'Этого ингредиента нет в базе'
INGREDIENTS_UNIQUE = 'Ингредиенты должны быть уникальными'

NO_TAGS = 'Добавьте теги'
TAGS_UNIQUE = 'Теги должны быть уникальными'

NO_IMAGE = 'Добавьте картинку'

RECIPE_NO_INGREDIENTS = 'Ингредиенты обязательны для рецепта'
RECIPE_NO_TAGS = 'Нужен хотя бы один тег'


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
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'is_subscribed',)

    @check_is_anonymous
    def get_is_subscribed(self, obj):
        return obj.following.filter(
            user=self.context.get('request').user
        ).exists()


class FoodUserCreateSerializer(UserCreateSerializer):
    email = serializers.EmailField(
        validators=(UniqueValidator(queryset=User.objects.all()),))

    class Meta:
        model = User
        fields = (
            'email',
            'id',
            'username',
            'first_name',
            'last_name',
            'password',)
        extra_kwargs = {
            'email': {'required': True},
            'username': {'required': True},
            'first_name': {'required': True},
            'last_name': {'required': True},
            'password': {'required': True}}


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
    author = FoodUserSerializer(read_only=True)
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
        read_only_fields = ('is_favorite', 'is_in_shopping_cart',) # 'id', 'tags', 'author',)
        # Разобраться с рид онли

    @check_is_anonymous
    def get_is_favorited(self, obj):
        return self.context.get(
            'request').user.favorite.filter(recipe=obj).exists()

    @check_is_anonymous
    def get_is_in_shopping_cart(self, obj):
        return self.context.get(
            'request').user.shoppingcart.filter(recipe=obj).exists()


class AddIngredientSerializer(serializers.ModelSerializer):

    id = serializers.IntegerField()
    # amount = serializers.IntegerField()

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'amount',)


class RecipeCreateSerializer(serializers.ModelSerializer):
    ingredients = AddIngredientSerializer(many=True,)
    # tags = serializers.PrimaryKeyRelatedField(
    #     queryset=Tag.objects.all(), many=True
    # )
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

    def validate_ingredients(self, value):
        if not value:
            raise ValidationError(NO_INGREDIENTS)
        ingredients = [
            ingredient_id['id']
            for ingredient_id
            in value]
        if len(ingredients) != len(set(ingredients)):
            raise ValidationError(INGREDIENTS_UNIQUE)
        return value

    def validate_tags(self, value):
        if not value:
            raise ValidationError(NO_TAGS)
        if len(value) != len(set(value)):
            raise ValidationError(TAGS_UNIQUE)
        return value

    def validate_image(self, value):
        if not value:
            raise ValidationError(NO_IMAGE)
        return value

    def set_ingredients(self, recipe, ingredients):
        for data in ingredients:
            try:
                RecipeIngredient.objects.create(
                    recipe=recipe,
                    ingredient=Ingredient.objects.get(id=data['id']),
                    amount=data['amount'])
            except ObjectDoesNotExist:
                raise ValidationError(NO_INGREDIENTS_DB)
        return recipe

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
    # recipes = RecipeCutFieldsSerializer(
    #     many=True, source='recipe', read_only=True)
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta(FoodUserSerializer.Meta):
        fields = FoodUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',)
        read_only_fields = ('username',)

    def get_recipes_count(self, author):
        return author.recipe.count()

    def get_recipes(self, obj):
        recipe = obj.recipe.all()
        limit = self.context.get('request').GET.get('recipes_limit')
        serializer = RecipeCutFieldsSerializer(
            recipe[:int(limit)] if limit else recipe,
            many=True, read_only=True)
        return serializer.data


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
