import random

# Create your models here.


class Card(object):

    def __init__(self, suit, rank):

        self.suit = self.validate_suit(suit)
        self.rank = self.validate_rank(rank)

    def validate_suit(self, suit):
        """
        :param suit: 
        :return: 
        """
        if suit in ('Clubs', 'Spades', 'Hearts', 'Diamonds'):
            return suit

        return f'invalid suit: {suit}'

    def validate_rank(self, rank):
        """
        :param rank: 
        :return: 
        """
        if type(rank) == int and rank > 0 and rank < 14:
            return rank

        return f'invalid rank: {rank}'

    def __str__(self):
        return f'{self.rank} of {self.suit}'

    def __repr__(self):
        return f'{self.rank} of {self.suit}'


class Deck(object):

    def __init__(self):
        self.deck = self.initialize_deck()

    def initialize_deck(self):
        deck = []
        for suit in ('Clubs', 'Spades', 'Hearts', 'Diamonds'):
            for rank in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
                deck.append(Card(suit=suit, rank=rank))

        random.shuffle(deck)

        return deck

    def shuffle(self):
        random.shuffle(self.deck)

    def cards_remaining(self):
        return len(self.deck)

    def deal(self):
        return self.deck.pop()

    def __str__(self):
        return f'deck with {self.cards_remaining()} cards remaining'

    def __repr__(self):
        return f'deck with {self.cards_remaining()} cards remaining'

if __name__ == '__main__':
    d = Deck()
    deck = d.deck
    print(d.cards_remaining())
    print(d.deal())
    print(d.cards_remaining())
    print(d)