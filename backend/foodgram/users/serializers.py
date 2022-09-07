from djoser.serializers import UserCreateSerializer, UserSerializer
from recipes.models import Recipe
from rest_framework import serializers
from rest_framework.generics import get_object_or_404

from .models import Follow, User


class UserSerializer(UserSerializer):
    is_following = serializers.SerializerMethodField(read_only=True)

    class Meta:
        model = User
        fields = (
            'id', 'first_name', 'last_name',
            'username', 'email', 'is_following'
        )

    def get_is_following(self, following):

        if self.context.get('request', ).user.is_anonymous:
            return False

        return Follow.objects.filter(
            user=self.context.get('request').user,
            following=following
        ).exists()


class UserCreateSerializer(UserCreateSerializer):
    class Meta:
        model = User
        fields = (
            'username', 'first_name', 'last_name', 'email', 'password'
        )


class FollowListSerializer(serializers.ModelSerializer):
    recipes = serializers.SerializerMethodField(
        method_name='get_recipes'
    )
    recipes_count = serializers.SerializerMethodField(
        method_name='get_recipes_count'
    )
    is_following = serializers.SerializerMethodField(
        method_name='get_is_following',
        read_only=True
    )

    class Meta:
        model = User
        fields = (
            'id', 'username', 'first_name', 'last_name', 'email',
            'is_following', 'recipes', 'recipes_count'
        )

    def get_recipes_count(self, following):
        return Recipe.objects.filter(author=following).count()

    def get_recipes(self, following):
        request = self.context.get('request')
        recipes_limit = request.get('recipes_limit')

        if not recipes_limit:
            return RecipeFollowingSerializer(
                following.author.all(),
                many=True, context={'request': request}
            ).data

        return RecipeFollowingSerializer(
            following.author.all()[:int(recipes_limit)], many=True,
            context={'request': request}
        ).data

    def get_is_following(self, following):
        return Follow.objects.filter(
            user=self.context.get('request').user,
            following=following
        ).exists()


class RecipeFollowingSerializer(serializers.ModelSerializer):

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):

    class Meta:
        model = Follow
        fields = ('user', 'following')

    def validate(self, data):
        get_object_or_404(User, username=data['following'])

        request = self.context.get('request')
        if request.user == data['following']:
            raise serializers.ValidationError('Подписка на себя запрещена')

        if Follow.objects.filter(
                user=self.context['request'].user,
                following=data['following']
        ):
            raise serializers.ValidationError(
                'Вы уже подписаны на этого пользователя')
        return data

    def follow_list(self, instance):
        return FollowListSerializer(
            instance.following,
            context={'request': self.context.get('request')}
        ).data
