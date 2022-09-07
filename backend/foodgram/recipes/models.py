from django.core.validators import MinValueValidator
from django.db import models
from users.models import User


class Ingredient(models.Model):

    name = models.CharField(
        'Название',
        max_length=200,
    )

    unit = models.CharField(
        'Единица измерения',
        max_length=200,
    )

    models.UniqueConstraint(fields=['name', 'unit'], name='unique_ingr_pair')

    class Meta:
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'
        ordering = ('name',)

    def __str__(self):
        return self.name


class Tag(models.Model):
    name = models.CharField(
        'Название',
        max_length=200,
    )
    color = models.CharField(
        'Цветовой HEX-код',
        max_length=7
    )
    slug = models.SlugField(
        'Slug',
        unique=True,
        max_length=200,
    )

    class Meta:
        verbose_name = 'Тэг'
        verbose_name_plural = 'Тэги'

    def __str__(self):
        return self.name


class Recipe(models.Model):

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='author',
        verbose_name='Автор'
    )

    name = models.CharField(
        max_length=200,
        db_index=True,
        verbose_name='Название'
    )

    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientsAmount',
        through_fields=('recipe', 'ingredient'),
        related_name='ingredients',
        verbose_name='Ингредиенты'
    )

    image = models.ImageField(
        upload_to='recipes/',
        verbose_name='Изображение')

    tags = models.ManyToManyField(Tag, verbose_name='Тэги')

    text = models.TextField(verbose_name='Описание')

    cooking_time = models.PositiveSmallIntegerField(
        validators=[MinValueValidator(
            1,
            message='Мин. время приготовления: 1 минута'
        )],
        verbose_name='Время приготовления'
    )

    class Meta:
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'
        ordering = ('-id',)

    def __str__(self):
        return self.name


class IngredientsAmount(models.Model):

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Рецепт'
    )

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        related_name='amount',
        verbose_name='Ингредиент'
    )

    amount = models.PositiveSmallIntegerField(
        verbose_name='Количество',
        validators=(
            MinValueValidator(
                1, message='Мин. количество: 1 единица'),),
    )

    class Meta:
        verbose_name = 'Количество ингредиента'
        verbose_name_plural = 'Количество ингредиентов'
        constraints = (
            models.UniqueConstraint(
                fields=['ingredient', 'recipe'],
                name='unique_ingredient'
            ),
        )


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorited',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorited',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Избранное'
        verbose_name_plural = 'Избранное'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_favorite'
            ),
        )


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Пользователь'
    )

    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='user_shopping_cart',
        verbose_name='Рецепт'
    )

    class Meta:
        verbose_name = 'Корзина покупок'
        verbose_name_plural = 'Корзина покупок'
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'recipe'],
                name='unique_shopping_cart'
            ),
        )

    def __str__(self):
        return f'{self.recipe.name}'
