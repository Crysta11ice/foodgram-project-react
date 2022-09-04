from django_filters.rest_framework import FilterSet, filters
from recipes.models import Recipe
from rest_framework.filters import SearchFilter


class RecipesFilter(FilterSet):
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )
    is_favorited = filters.BooleanFilter(method='get_is_favorited')
    tags = filters.AllValuesMultipleFilter(field_name='tags__slug')

    def get_is_favorited(self, arg, value, name):
        if not self.request.user.is_anonymous:
            if value:
                return arg.filter(favorited__user=self.request.user)

        return arg

    def get_is_in_shopping_cart(self, arg, value, name):
        if not self.request.user.is_anonymous:
            if value:
                return arg.filter(user_shopping_cart__user=self.request.user)

        return arg

    class Meta:
        model = Recipe
        fields = ('author', 'tags')


class IngredientFilter(SearchFilter):
    search_param = 'name'
