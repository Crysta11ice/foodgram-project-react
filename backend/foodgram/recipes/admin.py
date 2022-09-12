from django.contrib import admin

from .models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                     ShoppingCart, Tag)


@admin.register(IngredientsAmount)
class IngridientAmountAdmin(admin.ModelAdmin):
    list_display = (
        'recipe', 'ingredient', 'amount'
    )
    list_filter = ('recipe', 'ingredient')
    empty_value_display = '-пусто-'


class IngredientsAmountInLine(admin.TabularInline):
    model = IngredientsAmount


@admin.register(Recipe)
class RecipesAdmin(admin.ModelAdmin):
    list_display = ('name', 'author')
    readonly_fields = ('add_to_favorites',)
    list_filter = ('author', 'name', 'tags')
    list_per_page = 20
    inlines = [IngredientsAmountInLine]
    empty_value_display = '-пусто-'

    def add_to_favorites(self, obj):
        return obj.favorite.count()


@admin.register(Ingredient)
class IngredientsAdmin(admin.ModelAdmin):
    list_display = ('name', 'measurement_unit')
    list_filter = ('name',)
    empty_value_display = '-пусто-'


@admin.register(ShoppingCart)
class ShoppingCartAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'


@admin.register(Tag)
class TagsAdmin(admin.ModelAdmin):
    list_display = ('name', 'color')
    empty_value_display = '-пусто-'


@admin.register(Favorite)
class FavoriteAdmin(admin.ModelAdmin):
    list_display = ('user', 'recipe')
    list_filter = ('user', 'recipe')
    empty_value_display = '-пусто-'
