from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, status
from rest_framework.response import Response
from recipes.models import (
    Ingredient,
    Favorite,
    ShoppingCart,
    Recipe,
    RecipeIngredient,
    Tag,
)
from users.models import Subscription, User
from .filters import IngredientFilter
from .serializers import (
    FoodUserSerializer,
    IngredientSerializer,
    SubscriptionSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    RecipeCutFieldsSerializer,
    RecipeSerializer,
)
import io
from django.http import FileResponse
from reportlab.pdfgen import canvas
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont


# PDF write settings
START = 0
BIG_FONT = 20
SMALL_FONT = 13
COLUMN_0 = 70
COLUMN_1 = 220
COLUMN_2 = 270
LINE_0 = 750
LINE_1 = 700
NEXT_LINE = 20


class FoodUserViewSet(UserViewSet):

    @action(
        detail=False)
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete',))
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return Response(
                serializer.data, status=status.HTTP_201_CREATED)
        try:
            subscription = Subscription.objects.get(user=user, author=author)
        except ObjectDoesNotExist:
            return Response(
                {'errors': 'Вы не были подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST,)
        subscription.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class RecipeViewSet(ModelViewSet):

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
        try:
            model.objects.create(user=user, recipe=recipe)
        except IntegrityError:
            return Response(
                {'errors': 'Этот рецепт уже добавлен'},
                status=status.HTTP_400_BAD_REQUEST)
        return Response(
            self.get_serializer(recipe).data,
            status=status.HTTP_201_CREATED)

    def delete_recipe(self, user, recipe, model):
        try:
            state = model.objects.get(user=user, recipe=recipe)
        except ObjectDoesNotExist:
            return Response(
                {'errors': 'Что мертво умереть не может'},
                status=status.HTTP_400_BAD_REQUEST,)
        state.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    @action(
        detail=True,
        methods=('post', 'delete'))
    def favorite(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.add_recipe(user, recipe, Favorite)
        return self.delete_recipe(user, recipe, Favorite)

    @action(
        detail=True,
        methods=('post', 'delete'))
    def shopping_cart(self, request, pk):
        user = request.user
        recipe = get_object_or_404(Recipe, id=pk)
        if request.method == 'POST':
            return self.add_recipe(user, recipe, ShoppingCart)
        return self.delete_recipe(user, recipe, ShoppingCart)

    @action(
        detail=False)
    def download_shopping_cart(self, request):
        INGREDIENT = 'ingredient__name'
        UNIT = 'ingredient__measurement_unit'
        AMOUNT = 'amount'

        user = request.user
        if not user.shoppingcart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        buffer = io.BytesIO()
        doc = canvas.Canvas(buffer)
        pdfmetrics.registerFont(TTFont('Calibri', 'Calibri.ttf'))
        doc.setFont('Calibri', BIG_FONT)
        doc.drawString(
            COLUMN_0, LINE_0, 'Список ингредиентов:')
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=user
        ).values(INGREDIENT, UNIT,).annotate(amount=Sum(AMOUNT))
        doc.setFont('Calibri', SMALL_FONT)
        y = LINE_1
        for item in ingredients:
            doc.drawString(COLUMN_0, y, f'- {item[INGREDIENT]}',)
            doc.drawString(COLUMN_1, y, f'{str(item[AMOUNT])} {item[UNIT]}',)
            y -= NEXT_LINE
        doc.showPage()
        doc.save()
        buffer.seek(START)
        return FileResponse(
            buffer, as_attachment=True, filename='Shopping-list.pdf')


class IngredientViewSet(ModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('name',)
    pagination_class = None


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
