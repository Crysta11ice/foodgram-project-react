from django.db.models import Sum
from django.http import HttpResponse
from django_filters.rest_framework import DjangoFilterBackend
from recipes.models import (Favorite, Ingredient, IngredientsAmount, Recipe,
                            ShoppingCart, Tag)
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response

from .filters import IngredientFilter, RecipesFilter
from .pagination import FoodgramPaginator
from .permissions import AdminOwnerGuestPermissions
from .serializers import (FavoriteSerializer, IngredientSerializer,
                          RecipeGetSerializer, RecipePostSerializer,
                          ShoppingCartSerializer, TagSerializer)


class RecipeViewSet(viewsets.ModelViewSet):
    queryset = Recipe.objects.all()
    permission_classes = (AdminOwnerGuestPermissions,)
    filter_backends = (DjangoFilterBackend,)
    filter_class = RecipesFilter
    pagination_class = FoodgramPaginator

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
        methods=('POST', 'DELETE',),
        permission_classes=(IsAuthenticated,)
    )
    def favorite(self, request, pk):
        return self.post_or_delete(
            request,
            Favorite,
            FavoriteSerializer,
            pk
        )

    @action(
        detail=True,
        methods=('POST', 'DELETE',),
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
        methods=('GET',),
        permission_classes=(IsAuthenticated,)
    )
    def download_shopping_cart(self, request, pk=None):
        shopping_cart = []
        ingredients = IngredientsAmount.objects.filter(
            recipe__user_shopping_cart__user=request.user.id
        ).values(
            'ingredient__name',
            'ingredient__measurement_unit'
        ).annotate(amount=Sum('amount'))

        for num, ingredient in enumerate(ingredients, start=1):
            shopping_cart.append(
                f'\n{num}. {ingredient["ingredient__name"]}:'
                f' {ingredient["amount"]}'
                f'({ingredient["ingredient__measurement_unit"]})'
            )

        response = HttpResponse(shopping_cart, content_type='text')
        response['Content-Disposition'] = (
            'attachment;filename=shopping_cart.pdf'
        )

        return response


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Tag.objects.all().order_by('id')
    serializer_class = TagSerializer
    pagination_class = None


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    queryset = Ingredient.objects.all()
    permission_classes = (AllowAny, )
    serializer_class = IngredientSerializer
    filter_backends = (IngredientFilter,)
    search_fields = ('^name',)
    pagination_class = None
