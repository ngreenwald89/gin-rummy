# from login_app.models import UserProfileModel
from django.contrib.auth.models import User
from django.db import models

from game.rummy_utils import identify_melds, string_to_cards


# Create your models here.


class Token(models.Model):
    id = models.AutoField(primary_key=True)
    state = models.IntegerField()
    # isInUse = models.BooleanField()


class RummyPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hand = models.TextField()

    def __str__(self):
        return self.user.username

    def identify_melds(self):
        return identify_melds(self.string_to_hand())

    def string_to_hand(self):
        return string_to_cards(self.hand)


class RummyGame(models.Model):

    player1 = models.ForeignKey(RummyPlayer, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(RummyPlayer, related_name='player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(RummyPlayer, related_name='winner', on_delete=models.CASCADE, null=True)
    turn = models.ForeignKey(RummyPlayer, related_name='turn', on_delete=models.CASCADE)
    current_card = models.TextField()
    deck = models.TextField()
