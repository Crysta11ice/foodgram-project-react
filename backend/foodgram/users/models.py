from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    USER = "user"
    ADMIN = "admin"
    MODERATOR = "moderator"

    user_type = [
        (USER, "user"),
        (MODERATOR, "moderator"),
        (ADMIN, "admin"),
    ]

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username', 'first_name', 'last_name']

    username = models.CharField(
        max_length=150,
        unique=True,
    )
    first_name = models.CharField(max_length=150)
    last_name = models.CharField(max_length=150)
    email = models.EmailField(max_length=254, unique=True)

    class Meta:
        ordering = ('-username',)

    def __str__(self):
        return self.username


class Follow(models.Model):

    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='follower'
    )

    following = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name='following'
    )

    class Meta:
        constraints = (
            models.UniqueConstraint(
                fields=['user', 'following'],
                name='follow'
            ),
        )

    def __str__(self):
        return f'{self.username} follow for {self.following}'
