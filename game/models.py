# from login_app.models import UserProfileModel
from django.contrib.auth.models import User
from django.db import models
from django.db.models import Model

from game.rummy_utils import identify_melds, string_to_cards, string_to_card


# Create your models here.


class Token(Model):

    id = models.AutoField(primary_key=True)
    state = models.IntegerField()
    user0 = models.TextField()
    user1 = models.TextField()


class RummyPlayer(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # a hand should be no longer than 29 characters - that's 9 commas and 10 possibly two character numbers
    hand = models.CharField(max_length=29, blank=True, null=False, default='')

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
    loser = models.ForeignKey(RummyPlayer, related_name='loser', on_delete=models.CASCADE, null=True)
    turn = models.ForeignKey(RummyPlayer, related_name='turn', on_delete=models.CASCADE)
    current_card = models.CharField(max_length=2, blank=True, null=False, default='')
    # deck max_length: 51 commas + 52*2 possibly two digit integers = 51 + 104 = 155
    deck = models.CharField(max_length=155, blank=True, null=False, default='')
    # meld max_length: 20 cards, 19 commas, 6 | for 6 separate melds = 20*2 + 19 + 6 = 65
    melds = models.CharField(max_length=65, blank=True, null=False, default='')

    def meld_string_to_melds(self):
        """
        store melds as string:
            each meld separated by |
            each card in a meld separated by ,
        :return:
        """
        return list(map(string_to_cards, self.melds.split('|')))

    def deck_string_to_deck(self):
        return string_to_cards(self.deck)

    def current_card_string_to_card(self):
        return string_to_card(self.current_card)

    def append_meld(self, meld):
        """
        append a meld string to current meld string
        :param meld: already in string format (not a list of Card objects)
        :return:
        """
        melds = self.melds.split('|')
        melds.append(meld)
        self.melds = '|'.join(melds)
        self.save()

    def remove_meld(self, meld):
        melds = self.melds.split('|')
        melds.remove(meld)
        self.melds = '|'.join(melds)
        self.save()

    # this doesn't look right
    def is_winner(self):
        if self.turn.hand:
            return False
        else:
            return True


class GameLog(models.Model):

    game = models.ForeignKey(RummyGame, related_name='game', on_delete=models.CASCADE)
    turn = models.ForeignKey(RummyPlayer, related_name='player', on_delete=models.CASCADE)
    move_number = models.IntegerField()  # autoincrement?
    draw_option = models.TextField(choices=[('top_of_deck_card', 'top_of_deck_card'), ('current_card', 'current_card')])
    draw_card = models.CharField(max_length=2, blank=True, null=False, default='')
    meld_option = models.TextField(choices=[('play_meld', 'play_meld'), ('lay_off', 'lay_off'), ('continue_to_discard', 'continue_to_discard')])
    # meld_cards max_length: 12 commas + 13*2 possibly two digit integers = 12 + 26 = 38
    meld_cards = models.CharField(max_length=38, blank=True, null=False, default='')
    discard_card = models.CharField(max_length=2, blank=True, null=False, default='')


class PlayerStats(models.Model):
    game = models.ForeignKey(RummyGame, on_delete=models.CASCADE)
    winner = models.ForeignKey(RummyPlayer, related_name='game_winner', on_delete=models.CASCADE)
    loser = models.ForeignKey(RummyPlayer, related_name='game_loser', on_delete=models.CASCADE)
