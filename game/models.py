from django.db import models

from login_app.models import UserProfileModel
from django.contrib.auth.models import User
# Create your models here.


# class DeckField(models.TextField):
#     """
#     Deck of Cards stored as list of comma separated strings
#     """
#     # __metaclass__ = models.SubfieldBase
#
#     def __init__(self, *args, **kwargs):
#         self.token = kwargs.pop('token', ',')
#         super(DeckField).__init__(*args, **kwargs)
#
#     # def to_python(self, value):
#     #     if not value: return
#     #     if isinstance(value, list):
#     #         return value
#     #     return value.split(self.token)
#
#     def get_db_prep_value(self, value):
#         if not value: return
#         assert (isinstance(value, list) or isinstance(value, tuple))
#         return self.token.join([u's' for s in value])
#
#     def value_to_string(self, obj):
#         value = self._get_val_from_obj(obj)
#         return self.get_db_prep_value(value)
#
#     def from_db_value(self, value, expression, connection, context):
#         if value is None:
#             return value
#         if isinstance(value, list):
#             return value
#         return value.split(self.token)


# class CardField(models.TextField):
#     __metaclass__ = models.SubfieldBase
#
#     description = "Card"
#
#     def __init__(self, *args, **kwargs):
#         super().__init__(*args, **kwargs)
#
#     def to_python(self, value):
#         if not value: return
#         if isinstance(value, str):


# class HandField(models.TextField):
#     # __metaclass__ = models.SubfieldBase
#
#     name = 'Hand for Player'
#
#     def __init__(self, *args, **kwargs):
#         self.token = kwargs.pop('token', ',')
#         super(HandField).__init__(*args, **kwargs)
#
#     # def to_python(self, value):
#     #     if not value: return
#     #     if isinstance(value, list):
#     #         return value
#     #     return value.split(self.token)
#
#     def get_db_prep_value(self, value):
#         if not value: return
#         assert (isinstance(value, list) or isinstance(value, tuple))
#         return self.token.join([u's' for s in value])
#
#     def value_to_string(self, obj):
#         value = self._get_val_from_obj(obj)
#         return self.get_db_prep_value(value)
#
#     def from_db_value(self, value, expression, connection, context):
#         if value is None:
#             return value
#         if isinstance(value, list):
#             return value
#         return value.split(self.token)


class HandField(models.Field):
    "Implements comma-separated storage of lists"

    def __init__(self, separator=",", *args, **kwargs):
        self.separator = separator
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include kwarg if it's not the default
        if self.separator != ",":
            kwargs['separator'] = self.separator
        return name, path, args, kwargs


class RummyPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    hand = models.TextField()
    # hand = HandField()

    def __str__(self):
        return self.user.username


class DeckField(models.Field):
    "Implements comma-separated storage of lists"

    def __init__(self, separator=",", *args, **kwargs):
        self.separator = separator
        super().__init__(*args, **kwargs)

    def deconstruct(self):
        name, path, args, kwargs = super().deconstruct()
        # Only include kwarg if it's not the default
        if self.separator != ",":
            kwargs['separator'] = self.separator
        return name, path, args, kwargs


class RummyGame(models.Model):

    player1 = models.ForeignKey(RummyPlayer, related_name='player1', on_delete=models.CASCADE)
    player2 = models.ForeignKey(RummyPlayer, related_name='player2', on_delete=models.CASCADE)
    winner = models.ForeignKey(RummyPlayer, related_name='winner', on_delete=models.CASCADE, null=True)
    turn = models.ForeignKey(RummyPlayer, related_name='turn', on_delete=models.CASCADE)
    current_card = models.TextField()
    # deck = DeckField()
    deck = models.TextField()


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
