from django.urls import include, path
from rest_framework import routers
from .views import FoodUserViewSet, RecipeViewSet, TagViewSet


router_v1 = routers.DefaultRouter()
router_v1.register(r'users', FoodUserViewSet, basename='users')
router_v1.register(r'tags', TagViewSet)
router_v1.register(r'recipes', RecipeViewSet)


urlpatterns = [
    path('auth/', include('djoser.urls.authtoken')),
    path('', include('djoser.urls')),
    path('', include(router_v1.urls)),

]
