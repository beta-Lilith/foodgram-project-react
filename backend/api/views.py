from datetime import datetime

from django.http import FileResponse
from django.shortcuts import get_object_or_404
from djoser.views import UserViewSet
from rest_framework import permissions, status
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework.viewsets import ModelViewSet, ReadOnlyModelViewSet

from foodgram_project.settings import FILEFORMAT, FILENAME
from recipes.models import (Favorite, FoodUser, Ingredient, Recipe,
                            RecipeIngredient, ShoppingCart, Subscription, Tag)
from recipes.utils import make_doc
from .filters import IngredientFilter, RecipeFilter
from .permissions import IsAuthor, ReadOnly
from .serializers import (IngredientSerializer, RecipeCreateSerializer,
                          RecipeCutFieldsSerializer, RecipeSerializer,
                          SubscriptionSerializer, TagSerializer)

SELF_SUBSCRIPTION = 'Вы не можете подписаться на себя'
SUBSRIPTION_UNIQUE = 'Вы уже подписаны на этого автора'
DEL_SUBSRIPTION_UNIQUE = 'Вы не были подписаны на этого автора'

RECIPE_UNIQUE = 'Этот рецепт уже добавлен'
DEL_RECIPE_UNIQUE = 'Что мертво умереть не может'


class FoodUserViewSet(UserViewSet):

    def get_permissions(self):
        if self.action in ('me',):
            return (IsAuthenticated(),)
        return super().get_permissions()

    @action(
        detail=False,
        permission_classes=(IsAuthenticated,))
    def subscriptions(self, request):
        queryset = FoodUser.objects.filter(following__user=request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(IsAuthenticated,))
    def subscribe(self, request, id=None):
        author = get_object_or_404(FoodUser, id=id)
        user = request.user
        subscription = Subscription.objects.filter(user=user, author=author)
        if request.method == 'POST':
            if author == user:
                raise ValidationError(SELF_SUBSCRIPTION)
            if subscription.exists():
                raise ValidationError(SUBSRIPTION_UNIQUE)
            Subscription.objects.create(user=user, author=author)
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        if not subscription.exists():
            raise ValidationError(DEL_SUBSRIPTION_UNIQUE)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):
    filterset_class = RecipeFilter
    permission_classes = (ReadOnly | IsAuthenticated & IsAuthor,)

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredient__ingredient', 'tags',
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        if self.action in ('favorite', 'shopping_cart',):
            return RecipeCutFieldsSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)

    def add_recipe(self, user, recipe, model):
        if model.objects.filter(user=user, recipe=recipe).exists():
            raise ValidationError(RECIPE_UNIQUE)
        model.objects.create(user=user, recipe=recipe)
        return Response(
            self.get_serializer(recipe).data,
            status=status.HTTP_201_CREATED)

    def delete_recipe(self, user, recipe, model):
        recipe_in_model = model.objects.filter(user=user, recipe=recipe)
        if not recipe_in_model.exists():
            raise ValidationError(DEL_RECIPE_UNIQUE)
        recipe_in_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'))
    def favorite(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            return self.add_recipe(user, recipe, Favorite)
        return self.delete_recipe(user, recipe, Favorite)

    @action(
        detail=True,
        methods=('post', 'delete'))
    def shopping_cart(self, request, pk):
        recipe = get_object_or_404(Recipe, id=pk)
        user = request.user
        if request.method == 'POST':
            return self.add_recipe(user, recipe, ShoppingCart)
        return self.delete_recipe(user, recipe, ShoppingCart)

    @action(
        detail=False)
    def download_shopping_cart(self, request):
        date = datetime.today().date()
        user = request.user
        if not user.shoppingcarts.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.get_shopping_cart_ingredients(user)
        recipes = RecipeIngredient.get_shopping_cart_recipes(user)
        doc = make_doc(ingredients, recipes, date)
        return FileResponse(
            doc, content_type=FILEFORMAT, as_attachment=True,
            filename=FILENAME.format(date))


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    pagination_class = None


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
