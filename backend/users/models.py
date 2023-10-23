from django.contrib.auth import get_user_model
from django.db import models


User = get_user_model()


class Subscription(models.Model):
    user = models.ForeignKey(
        User,
        verbose_name='подписчик',
        related_name='follower',
        on_delete=models.CASCADE,
    )
    author = models.ForeignKey(
        User,
        verbose_name='автор',
        related_name='following',
        on_delete=models.CASCADE,
    )

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
