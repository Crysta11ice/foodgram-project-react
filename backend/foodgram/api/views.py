from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (FavoriteRecipe, Ingredient, IngredientsAmount,
                            Recipe, ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipeFilter
from .pagination import FoodgramPaginator
from .permissions import AdminOwnerGuestPermissions
from .serializers import (FavoriteRecipesSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          ShoppingCartSerializer, TagSerializer)


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    ingredients = Ingredient.objects.all().order_by('name')
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    tags = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer


class RecipeViewSet(viewsets.ModelViewSet):
    recipes = Recipe.objects.all().order_by('-id')
    permission_classes = (AdminOwnerGuestPermissions,)
    pagination_class = FoodgramPaginator
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return RecipeGetSerializer
        return RecipePostSerializer

    @staticmethod
    def post_or_delete(request, model, serializer, pk):
        if request.method != 'POST':
            get_object_or_404(
                model,
                user=request.user,
                recipe=get_object_or_404(Recipe, id=pk)
            ).delete()
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = serializer(
            data={'user': request.user.id, 'recipe': pk},
            context={'request': request})
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.post_or_delete(
            request,
            FavoriteRecipe,
            FavoriteRecipesSerializer,
            pk
        )

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def shopping_cart(self, request, pk):
        return self.post_or_delete(
            request,
            ShoppingCart,
            ShoppingCartSerializer,
            pk
        )

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, pk=None):
        ingredients = IngredientsAmount.objects.filter(
            recipe__user_shopping_cart__user=request.user.id
        ).values(
            'ingredient__name',
            'ingredient__unit'
        ).annotate(amount=Sum('amount'))

        shopping_cart = ['Список покупок:\n--------------']

        for position, ingredient in enumerate(ingredients, start=1):
            shopping_cart.append(
                f'\n{position}. {ingredient["ingredient__name"]}:'
                f' {ingredient["amount"]}'
                f'({ingredient["ingredient__unit"]})'
            )

        response = HttpResponse(shopping_cart, content_type='text')
        response['Content-Disposition'] = (
            'attachment;filename=shopping_cart.pdf'
        )

        return response
