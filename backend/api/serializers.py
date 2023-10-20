from rest_framework import serializers

from recipes.models import Ingredient, Tag, Recipe, RecipeIngredient


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class RecipeIngredientSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField(
        source='ingredient.id'
    )
    name = serializers.ReadOnlyField(
        source='ingredient.name'
    )
    measurement_unit = serializers.ReadOnlyField(
        source='ingredient.measurement_unit'
    )

    class Meta:
        model = RecipeIngredient
        fields = ('id', 'name', 'measurement_unit', 'amount')


class RecipeSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True)
    ingredients = RecipeIngredientSerializer(
        many=True,
        source='recipe_ingredient',
    )

    class Meta:
        model = Recipe
        fields = (
            'id',
            'tags',
            'author',
            'ingredients',
            'name',
            'text',
            'cooking_time',
        )


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

    class Meta:
        model = Recipe
        fields = (
            'id',
            'ingredients',
            'tags',
            'name',
            'text',
            'cooking_time',
        )

    def set_ingredients(self, recipe, ingredients):
        for data in ingredients:
            RecipeIngredient.objects.create(
                recipe=recipe,
                ingredient=Ingredient.objects.get(id=data['id']),
                amount=data['amount'],
            )
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
