import random
from game.rummy_utils import Deck


class Player(object):
    def __init__(self, name='defaultPlayer'):
        self.name = name
        self.hand = []

    def __str__(self):
        return f'Player: {self.name}'

    def __repr__(self):
        return f'Player: {self.name}'


class Game(object):
    def __init__(self, player1, player2):

        self.deck = Deck()
        self.player1 = player1
        self.player2 = player2
        self.game_over = False

        self.start_game_deal()
        self.current_card = self.deal_from_deck()
        self.turn = random.choice([self.player1, self.player2])

    def start_game_deal(self):
        """
        distribute cards to players at start of game
        :return: 
        """
        for i in range(10):
            self.player1.hand.append(self.deal_from_deck())
            self.player2.hand.append(self.deal_from_deck())

    def deal_from_deck(self):
        if self.deck:
            return self.deck.deal()

        return "No cards left in Deck"

    def is_game_over(self):
        """
        check if player has Gin
        :return: 
        """
        pass