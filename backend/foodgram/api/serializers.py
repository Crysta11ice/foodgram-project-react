from drf_extra_fields.fields import Base64ImageField
from recipes.models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import serializers
from users.serializers import UserSerializer


class IngredientSerializer(serializers.ModelSerializer):
    class Meta:
        model = Ingredient
        fields = ('id', 'name', 'unit')


class TagSerializer(serializers.ModelSerializer):
    class Meta:
        model = Tag
        fields = ('id', 'name', 'color', 'slug')


class IngredientsAmountGetSerializer(serializers.ModelSerializer):
    name = serializers.CharField(source='ingredient.name', read_only=True)
    unit = serializers.CharField(
        source='ingredient.unit', read_only=True
    )
    id = serializers.IntegerField(source='ingredient.id', read_only=True)

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'name', 'unit', 'amount')


class IngredientsAmountPostSerializer(serializers.ModelSerializer):
    id = serializers.PrimaryKeyRelatedField(
        queryset=Ingredient.objects.all()
    )
    amount = serializers.IntegerField(min_value=1)

    class Meta:
        model = IngredientsAmount
        fields = ('id', 'amount')


class RecipeGetSerializer(serializers.ModelSerializer):
    tags = TagSerializer(many=True, read_only=True)
    author = UserSerializer(read_only=True)
    ingredients = serializers.SerializerMethodField(
        method_name='get_ingredients'
    )
    is_favorited = serializers.SerializerMethodField(
        method_name='get_is_favorited',
        read_only=True
    )
    is_in_shopping_cart = serializers.SerializerMethodField(
        method_name='get_is_in_shopping_cart',
        read_only=True
    )

    class Meta:
        model = Recipe
        fields = (
            'id', 'name', 'author', 'ingredients', 'text', 'image',
            'tags', 'is_favorited', 'is_in_shopping_cart', 'cooking_time'
        )

    def get_ingredients(self, recipe):
        return IngredientsAmountGetSerializer(
            IngredientsAmount.objects.filter(recipe=recipe),
            many=True
        ).data

    def get_is_favorited(self, recipe):
        if self.context.get('request').user.is_anonymous:
            return False
        return Favorite.objects.filter(
            user=self.context.get('request').user,
            recipe=recipe
        ).exists()

    def get_is_in_shopping_cart(self, recipe):
        if self.context.get('request').user.is_anonymous:
            return False
        return ShoppingCart.objects.filter(
            user=self.context.get('request').user,
            recipe=recipe
        ).exists()


class RecipePostSerializer(serializers.ModelSerializer):
    author = UserSerializer(read_only=True)
    ingredients = IngredientsAmountPostSerializer(many=True)
    tags = serializers.PrimaryKeyRelatedField(
        queryset=Tag.objects.all(), many=True)
    image = Base64ImageField()

    class Meta:
        model = Recipe
        fields = ('id', 'author', 'ingredients', 'tags',
                  'image', 'name', 'text', 'cooking_time')

    @staticmethod
    def create_ingredients_tags(recipe, ingredients, tags):
        for ingredient in ingredients:
            IngredientsAmount.objects.create(
                recipe=recipe,
                ingredient=ingredient['id'],
                amount=ingredient['amount']
            )
        for tag in tags:
            recipe.tags.add(tag)

    def create(self, validated_data):
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        recipe = Recipe.objects.create(
            author=self.context.get('request').user,
            **validated_data
        )
        self.create_ingredients_tags(recipe, ingredients, tags)
        return recipe

    def update(self, recipe, validated_data):
        recipe.tags.clear()
        IngredientsAmount.objects.filter(recipe=recipe).delete()
        ingredients = validated_data.pop('ingredients')
        tags = validated_data.pop('tags')
        self.create_ingredients_tags(recipe, ingredients, tags)
        return super().update(recipe, validated_data)

    def validate(self, data):
        ingredients = self.initial_data.get('ingredients')
        ingredient = data['ingredients']
        if not ingredient:
            raise serializers.ValidationError({
                'В рецепте должен быть хотя бы один ингредиент'
            })
        ingredients_list = []
        for ingredient in ingredients:
            ingredient_id = ingredient['id']
            if ingredient_id in ingredients_list:
                raise serializers.ValidationError({
                    'ingredient': 'Ингредиент должен быть уникален'
                })
            ingredients_list.append(ingredient_id)
            amount = ingredient['amount']
            if int(amount) <= 0:
                raise serializers.ValidationError({
                    'amount': 'Количество ингредиента должно быть больше 0'
                })
        cooking_time = data['cooking_time']
        if int(cooking_time) <= 0:
            raise serializers.ValidationError({
                'cooking_time': 'Время приготовления должно быть больше 0'
            })
        return data


class FavoriteSerializer(serializers.ModelSerializer):
    class Meta:
        model = Favorite
        fields = ('user', 'recipe')

    def validate(self, data):
        if Favorite.objects.filter(
                user=self.context.get('request').user,
                recipe=data['recipe']
        ).exists():
            raise serializers.ValidationError({
                'status': 'Рецепт уже в избранном'
            })
        return data


class RecipeViewSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class ShoppingCartSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCart
        fields = ('user', 'recipe')

    def validate(self, data):
        if ShoppingCart.objects.filter(
                user=self.context['request'].user,
                recipe=data['recipe']
        ):
            raise serializers.ValidationError('Рецепт уже в корзине')
        return data
