from django.contrib.auth.models import AbstractUser
from django.core.validators import MinValueValidator, RegexValidator
from django.db import models
from django.db.models import F, Sum

from foodgram_project.settings import LENGTHS

from .validators import validate_username

NOT_UNIQUE_NAME = {'unique': "Это имя пользователя уже существует."}

HEX_VALIDATION = 'Введите цвет в формате HEX'

COOK_MIN = 1
COOK_ERROR = 'Минимальное значение = 1'

AMOUNT_MIN = 1
AMOUNT_ERROR = 'Минимальное значение = 1'


class FoodUser(AbstractUser):
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ('username', 'first_name', 'last_name',)
    email = models.EmailField(
        'электронная почта',
        max_length=LENGTHS['EMAIL'],
        unique=True)
    username = models.CharField(
        'логин',
        max_length=LENGTHS['USERNAME'],
        unique=True,
        validators=(validate_username,),
        error_messages=NOT_UNIQUE_NAME)
    first_name = models.CharField(
        'имя',
        max_length=LENGTHS['FIRST_NAME'])
    last_name = models.CharField(
        'фамилия',
        max_length=LENGTHS['LAST_NAME'])

    class Meta:
        verbose_name = 'пользователь'
        verbose_name_plural = 'пользователи'
        ordering = ('username',)

    def __str__(self):
        return self.username


class Subscription(models.Model):
    user = models.ForeignKey(
        FoodUser,
        verbose_name='подписчик',
        related_name='follower',
        on_delete=models.CASCADE)
    author = models.ForeignKey(
        FoodUser,
        verbose_name='автор',
        related_name='following',
        on_delete=models.CASCADE)

    class Meta:
        verbose_name = 'подписка'
        verbose_name_plural = 'подписки'
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'author',),
                name='unique_subscription'
            )]

    def __str__(self):
        return f'{self.user} подписался на {self.author}'


class Tag(models.Model):
    name = models.CharField(
        'имя',
        max_length=LENGTHS['TAG_NAME'])
    color = models.CharField(
        'цвет',
        max_length=LENGTHS['TAG_COLOR'],
        validators=[RegexValidator(
            regex='^#[0-9a-fA-F]{6}$',
            message=HEX_VALIDATION)])
    slug = models.SlugField(
        'тег',
        max_length=LENGTHS['TAG_SLUG'],
        unique=True)

    class Meta:
        verbose_name = 'тег'
        verbose_name_plural = 'теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    name = models.CharField(
        'название',
        max_length=LENGTHS['INGREDIENT_NAME'])
    measurement_unit = models.CharField(
        'единица измерения',
        max_length=LENGTHS['INGREDIENT_MEASURE'])

    class Meta:
        verbose_name = 'продукт'
        verbose_name_plural = 'продукты'
        ordering = ('name',)
        constraints = [
            models.UniqueConstraint(
                fields=('name', 'measurement_unit',),
                name='unique_ingredient',
            )]

    def __str__(self):
        return f'{self.name} ({self.measurement_unit})'


class Recipe(models.Model):
    tags = models.ManyToManyField(
        Tag,
        verbose_name='тег',
        related_name='recipe')
    author = models.ForeignKey(
        FoodUser,
        verbose_name='автор',
        related_name='recipe',
        on_delete=models.CASCADE)
    ingredients = models.ManyToManyField(
        Ingredient,
        verbose_name='продукт',
        related_name='recipe',
        through='RecipeIngredient',
        through_fields=('recipe', 'ingredient'))
    name = models.CharField(
        'название',
        max_length=LENGTHS['RECIPE_NAME'])
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
        verbose_name='продукт',
        related_name='recipe_ingredient',
        on_delete=models.CASCADE)
    amount = models.PositiveIntegerField(
        'мера',
        validators=(MinValueValidator(AMOUNT_MIN, AMOUNT_ERROR),))

    @staticmethod
    def get_shopping_cart_ingredients(user):
        return RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=user
        ).values(
            name=F('ingredient__name'),
            unit=F('ingredient__measurement_unit'),
        ).annotate(amount=Sum('amount'))

    @staticmethod
    def get_shopping_cart_recipes(user):
        return RecipeIngredient.objects.filter(
            recipe__shoppingcarts__user=user
        ).values(
            name=F('recipe__name'))

    class Meta:
        verbose_name = 'продукт в рецепте'
        verbose_name_plural = 'продукты в рецепте'

    def __str__(self):
        return self.recipe.name


class UserRecipe(models.Model):
    user = models.ForeignKey(
        FoodUser,
        verbose_name='пользователь',
        related_name='%(class)ss',
        on_delete=models.CASCADE)
    recipe = models.ForeignKey(
        Recipe,
        verbose_name='рецепт',
        related_name='%(class)ss',
        on_delete=models.CASCADE)

    class Meta:
        abstract = True
        constraints = [
            models.UniqueConstraint(
                fields=('user', 'recipe',),
                name='unique_%(class)s',
            )]

    def __str__(self):
        return f'{self.user} добавил {self.recipe}'


class Favorite(UserRecipe):

    class Meta(UserRecipe.Meta):
        verbose_name = 'избранное'
        verbose_name_plural = 'избранное'


class ShoppingCart(UserRecipe):

    class Meta(UserRecipe.Meta):
        verbose_name = 'корзина'
        verbose_name_plural = 'корзина'
