from django.db import IntegrityError
from django.db.models import Sum
from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.exceptions import ValidationError
from rest_framework.viewsets import ReadOnlyModelViewSet, ModelViewSet
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
from .filters import IngredientFilter, RecipeFilter
from .permissions import ReadOnly, IsAdmin, IsAuthor
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

from foodgram_project.settings import (
    START,
    BIG_FONT,
    SMALL_FONT,
    BIG_FONT_SIZE,
    SMALL_FONT_SIZE,
    COLUMN_0,
    COLUMN_1,
    LINE_0,
    LINE_1,
    TEXT_0,
    NEXT_LINE)
from rest_framework.permissions import (
    IsAuthenticatedOrReadOnly,
    IsAuthenticated,
    AllowAny
)


class FoodUserViewSet(UserViewSet):

    @action(
        detail=False,
        permission_classes=(IsAuthor | IsAdmin,))
    def me(self, request, *args, **kwargs):
        return super().me(request, *args, **kwargs)

    @action(
        detail=False,
        permission_classes=(IsAuthor | IsAdmin,))
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request})
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete',),
        permission_classes=(IsAuthor | IsAdmin,))
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            if author == user:
                return Response(
                    {'errors': 'Вы не можете подписаться на себя'},
                    status=status.HTTP_400_BAD_REQUEST)
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request})
            serializer.is_valid(raise_exception=True)
            try:
                Subscription.objects.create(user=user, author=author)
            except IntegrityError:
                return Response(
                    {'errors': 'Вы уже подписаны на этого автора'},
                    status=status.HTTP_400_BAD_REQUEST)
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
    filterset_class = RecipeFilter
    permission_classes = (ReadOnly | IsAuthor | IsAdmin,)

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
            raise ValidationError('Этот рецепт уже добавлен')
        model.objects.create(user=user, recipe=recipe)
        return Response(
            self.get_serializer(recipe).data,
            status=status.HTTP_201_CREATED)

    def delete_recipe(self, user, recipe, model):
        recipe_in_model = model.objects.filter(user=user, recipe=recipe)
        if not recipe_in_model.exists():
            raise ValidationError('Что мертво умереть не может')
        recipe_in_model.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)

    def make_doc(self, buffer, ingredients, INGREDIENT, AMOUNT, UNIT):
        doc = canvas.Canvas(buffer)
        doc.setFont(BIG_FONT, BIG_FONT_SIZE)
        doc.drawString(COLUMN_0, LINE_0, TEXT_0)
        doc.setFont(SMALL_FONT, SMALL_FONT_SIZE)
        y = LINE_1
        for item in ingredients:
            doc.drawString(COLUMN_0, y, f'- {item[INGREDIENT]}',)
            doc.drawString(COLUMN_1, y, f'{str(item[AMOUNT])} {item[UNIT]}',)
            y -= NEXT_LINE
        doc.showPage()
        doc.save()

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
        INGREDIENT = 'ingredient__name'
        UNIT = 'ingredient__measurement_unit'
        AMOUNT = 'amount'

        user = request.user
        if not user.shoppingcart.exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ingredients = RecipeIngredient.objects.filter(
            recipe__shoppingcart__user=user
        ).values(INGREDIENT, UNIT,).annotate(amount=Sum(AMOUNT))
        buffer = io.BytesIO()
        self.make_doc(buffer, ingredients, INGREDIENT, AMOUNT, UNIT)
        buffer.seek(START)
        return FileResponse(
            buffer, as_attachment=True, filename='Shopping-list.pdf')


class IngredientViewSet(ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    filterset_class = IngredientFilter
    pagination_class = None
    # permission_classes = (ReadOnly | IsAdmin,)


class TagViewSet(ReadOnlyModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    pagination_class = None
    # permission_classes = (ReadOnly | IsAdmin,)
