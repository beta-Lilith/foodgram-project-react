from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


TAG_NAME_LENGTH = 200
TAG_COLOR_LENGTH = 7
TAG_SLUG_LENGTH = 200

RECIPE_NAME_LENGTH = 200

INGREDIENT_NAME_LENGTH = 200
INGREDIENT_MEASURE_LENGTH = 200

COOK_MIN = 1
COOK_ERROR = 'Минимальное значение = 1'

AMOUNT_MIN = 1
AMOUNT_ERROR = 'Минимальное значение = 1'


class Tag(models.Model):
    name = models.CharField(
        'имя',
        max_length=TAG_NAME_LENGTH)
    color = models.CharField(
        'цвет',
        max_length=TAG_COLOR_LENGTH)
    slug = models.SlugField(
        'URL-адрес',
        max_length=TAG_COLOR_LENGTH,
        unique=True)

    class Meta:
        verbose_name = 'тэг'
        verbose_name_plural = 'тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тэг',
        related_name='recipe')
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        related_name='recipe',
        on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        'Ingredient',
        verbose_name='ингредиент',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'))
    name = models.CharField(
        'название',
        max_length=RECIPE_NAME_LENGTH)
    image = models.ImageField(
        'изображение',
        upload_to='recipe_images/')
    text = models.TextField(
        'рецепт')
    cooking_time = models.PositiveIntegerField(
        'время приготовления',
        validators=(MinValueValidator(COOK_MIN, COOK_ERROR),))

    class Meta:
        verbose_name = 'рецепт'
        verbose_name_plural = 'рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'название',
        max_length=INGREDIENT_NAME_LENGTH)
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=INGREDIENT_MEASURE_LENGTH)

    class Meta:
        verbose_name = 'ингредиент'
        verbose_name_plural = 'ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class RecipeIngredient(models.Model):
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        related_name='recipe_ingredient',
        on_delete=models.CASCADE)
    ingredient = models.ForeignKey(
        Ingredient,
        verbose_name='ингредиент',
        # related_name='recipe_ingredient',
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        'количество',
        validators=(MinValueValidator(AMOUNT_MIN, AMOUNT_ERROR),))

    class Meta:
        verbose_name = 'Ингредиент в рецепте'
        verbose_name_plural = 'Ингредиенты в рецепте'

    def __str__(self):
        return self.recipe.name


class UserRecipe(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='пользователь',
        related_name='%(class)s',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        related_name='%(class)s',
        on_delete=models.CASCADE)

    class Meta:
        abstract = True

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'


class Favorite(UserRecipe):

    class Meta:
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_favorite',
            )]


class ShoppingCart(UserRecipe):

    class Meta:
        verbose_name = 'корзина'
        verbose_name_plural = 'корзина'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_shopping_cart',
            )]
