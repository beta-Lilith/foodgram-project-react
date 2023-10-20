from django.shortcuts import render
from djoser.views import UserViewSet
from rest_framework.viewsets import ModelViewSet
from rest_framework import permissions
from recipes.models import Recipe, Tag
from .serializers import TagSerializer, RecipeCreateSerializer, RecipeSerializer


class FoodUserViewSet(UserViewSet):
    pass


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
