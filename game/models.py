from django.db import models

from login_app.models import UserProfileModel
from django.contrib.auth.models import User
# Create your models here.


class DeckField(models.Field):

    description = "Deck of cards for a given game"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class CardField(models.Field):

    description = "Card"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class HandField(models.Field):

    description = "Hand of cards for a given player"

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)


class RummyPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hand = HandField()

    def __str__(self):
        return self.user.username


class RummyGame(models.Model):

    player1 = models.ForeignKey(RummyPlayer, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(RummyPlayer, related_name='player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(RummyPlayer, related_name='winner', on_delete=models.CASCADE)
    turn = models.ForeignKey(RummyPlayer, related_name='turn', on_delete=models.CASCADE)
    deck = DeckField()
    current_card = CardField()


class RummyCard(models.Model):

    SUIT_CHOICES = (
        ('Hearts', 'Hearts'),
        ('Diamonds', 'Diamonds'),
        ('Clubs', 'Clubs'),
        ('Spades', 'Spades'),
    )
    RANK_CHOICES = (
        (1, 1),
        (2, 2),
        (3, 3),
        (4, 4),
        (5, 5),
        (6, 6),
        (7, 7),
        (8, 8),
        (9, 9),
        (10, 10),
        (11, 11),
        (12, 12),
        (13, 13),
    )

    suit = models.TextField(choices=SUIT_CHOICES)
    rank = models.IntegerField(choices=RANK_CHOICES)


# class Deck(models.Model):
#
#
#
#     @property
#     def initialize_deck(self):
#         deck = []
#         for suit in ('club', 'heart', 'spade', 'diamond'):
#             for rank in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
#                 deck.append(Card(suit=suit, rank=rank))
#
#         return deck
#
#     @property
#     def shuffle(self):
#         # shuffles list in place, does not return new object
#         random.shuffle(self.deck)
