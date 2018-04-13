from django.db import models

from login_app.models import UserProfileModel
from django.contrib.auth.models import User
# Create your models here.


class RummyPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hand = models.TextField()
    # hand = HandField()

    def __str__(self):
        return self.user.username


class RummyGame(models.Model):

    player1 = models.ForeignKey(RummyPlayer, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(RummyPlayer, related_name='player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(RummyPlayer, related_name='winner', on_delete=models.CASCADE, null=True)
    turn = models.ForeignKey(RummyPlayer, related_name='turn', on_delete=models.CASCADE)
    current_card = models.TextField()
    # deck = DeckField()
    deck = models.TextField()
