from api.pagination import FoodgramPaginator
from api.permissions import AdminOwnerGuestPermissions
from djoser.views import UserViewSet
from rest_framework import status
from rest_framework.decorators import action
from rest_framework.generics import get_object_or_404
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response

from .models import Follow, User
from .serializers import FollowListSerializer, FollowSerializer, UserSerializer


class UserViewSet(UserViewSet):
    pagination_class = FoodgramPaginator
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = AdminOwnerGuestPermissions

    @action(
        detail=True,
        methods=['POST', 'DELETE'],
        permission_classes=(IsAuthenticated,)
    )
    def subscribe(self, request, id):
        if request.method != 'POST':
            follow = get_object_or_404(
                Follow,
                following=get_object_or_404(User, id=id),
                user=request.user
            )
            self.perform_destroy(follow)
            return Response(status=status.HTTP_204_NO_CONTENT)

        serializer = FollowSerializer(
            data={
                'user': request.user.id,
                'following': get_object_or_404(User, id=id).id
            },
            context={'request': request}
        )

        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(
        detail=False,
        methods=['GET'],
        permission_classes=(IsAuthenticated, )
    )
    def subscriptions(self, request, pk=None):
        follow_list = self.paginate_queryset(
            User.objects.filter(following__user=request.user)
        )

        serializer = FollowListSerializer(
            follow_list, many=True, context={
                'request': request
            }
        )

        return self.get_paginated_response(serializer.data)
