from django.shortcuts import get_object_or_404
from django.core.exceptions import ObjectDoesNotExist
from djoser.views import UserViewSet
from rest_framework.decorators import action
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions, response, status
from recipes.models import Recipe, Tag
from users.models import User, Subscription
from .serializers import (
    FoodUserSerializer,
    SubscriptionSerializer,
    TagSerializer,
    RecipeCreateSerializer,
    RecipeSerializer,
)


class FoodUserViewSet(UserViewSet):
    @action(
        detail=False,
    )
    def subscriptions(self, request):
        queryset = User.objects.filter(following__user=request.user)
        serializer = SubscriptionSerializer(
            self.paginate_queryset(queryset),
            many=True,
            context={'request': request},
        )
        return self.get_paginated_response(serializer.data)

    @action(
        detail=True,
        methods=('post', 'delete',),
    )
    def subscribe(self, request, id=None):
        author = get_object_or_404(User, id=id)
        user = request.user
        if request.method == 'POST':
            serializer = SubscriptionSerializer(
                author,
                data=request.data,
                context={'request': request},
            )
            serializer.is_valid(raise_exception=True)
            Subscription.objects.create(user=user, author=author)
            return response.Response(
                serializer.data, status=status.HTTP_201_CREATED
            )
        try:
            subscription = Subscription.objects.get(user=user, author=author)
        except ObjectDoesNotExist:
            return response.Response(
                {'errors': 'Вы не были подписаны на этого автора'},
                status=status.HTTP_400_BAD_REQUEST,
            )
        subscription.delete()
        return response.Response(status=status.HTTP_204_NO_CONTENT)


class TagViewSet(ModelViewSet):
    queryset = Tag.objects.all()
    serializer_class = TagSerializer


class RecipeViewSet(ModelViewSet):
    queryset = Recipe.objects.all()
    # serializer_class = RecipeSerializer

    def get_queryset(self):
        recipes = Recipe.objects.prefetch_related(
            'recipe_ingredient__ingredient', 'tags',
        ).all()
        return recipes

    def get_serializer_class(self):
        if self.request.method in permissions.SAFE_METHODS:
            return RecipeSerializer
        return RecipeCreateSerializer

    def perform_create(self, serializer):
        serializer.save(author=self.request.user)
