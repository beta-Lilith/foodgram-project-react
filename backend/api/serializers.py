from rest_framework import serializers
from rest_framework.validators import UniqueValidator
from djoser.serializers import UserSerializer, UserCreateSerializer
from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient
from users.models import Subscription, User
from drf_extra_fields.fields import Base64ImageField


def check_is_anonymous(func):
    def wrapper(self, author):
        user = self.context.get('request').user
        if user.is_anonymous:
            return False
        return func(self, author)
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
    def get_is_subscribed(self, author):
        return author.following.filter(
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
        read_only_fields = ('is_favorite', 'is_in_shopping_cart', 'id', 'tags', 'author')
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
    ingredients = AddIngredientSerializer(many=True)
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

    def set_ingredients(self, recipe, ingredients):
        for data in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=data['id']),
                amount=data['amount'])
        return recipe

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = super().create(validated_data)
        self.set_ingredients(recipe, ingredients)
        recipe.tags.set(tags)
        return recipe

    def update(self, recipe, validated_data):
        ingredients = validated_data.pop('ingredients')
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
    recipes = RecipeCutFieldsSerializer(
        many=True, source='recipe', read_only=True)
    recipes_count = serializers.SerializerMethodField()

    class Meta(FoodUserSerializer.Meta):
        fields = FoodUserSerializer.Meta.fields + (
            'recipes',
            'recipes_count',)
        read_only_fields = ('username',)

    def get_recipes_count(self, author):
        return author.recipe.count()


class IngredientSerializer(serializers.ModelSerializer):

    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'measurement_unit',)
