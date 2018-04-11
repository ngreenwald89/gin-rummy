import random

RANK_MAP = {
        1: 'Ace',
        11: 'Jack',
        12: 'Queen',
        13: 'King'
    }

SUIT_MAP = {
    'C': 'Clubs',
    'S': 'Spades',
    'H': 'Hearts',
    'D': 'Diamonds',
}

SUIT_VAL = {
    'C': 0,
    'S': 1,
    'H': 2,
    'D': 3,
}

REVERSE_SUIT_VAL = {
    0: 'C',
    1: 'S',
    2: 'H',
    3: 'D',
}


class Card(object):

    def __init__(self, suit, rank):

        self.suit = self.validate_suit(suit)
        self.rank = self.validate_rank(rank)

    def validate_suit(self, suit):
        """
        :param suit: 
        :return: 
        """
        if suit in ('C', 'S', 'H', 'D'):
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

    def as_number(self):

        return self.rank + SUIT_VAL[self.suit] * 13

    def card_to_string(self):
        return str(self.as_number())

    def __str__(self):
        return f'{RANK_MAP.get(self.rank, self.rank)} of {SUIT_MAP.get(self.suit)}'

    def __repr__(self):
        return f'{RANK_MAP.get(self.rank, self.rank)} of {SUIT_MAP.get(self.suit)}'


def string_to_card(num_string):
    """
    gets number of card as stored in db as number string
    :param num_string: 
    :return: 
    """
    num = int(num_string)
    if num % 13 == 0:
        suit = (num // 13) - 1
        rank = 13
    else:
        suit, rank = divmod(num, 13)

    return Card(suit=REVERSE_SUIT_VAL[suit], rank=rank)



class Deck(object):
    def __init__(self):
        self.deck = self.initialize_deck()

    def initialize_deck(self):
        deck = []
        for suit in ('C', 'S', 'H', 'D'):
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


def validate_meld(cards):
    """

    :param cards: 
    :return: Boolean
    """
    return validate_same_rank(cards) or validate_run(cards)


def validate_same_rank(cards):
    if len(cards) not in (3, 4):
        return False
    return all(card.rank == cards[0].rank for card in cards)


def validate_run(cards):
    if len(cards) < 3:
        return False
    if not all(card.suit == cards[0].suit for card in cards):
        return False

    ranks = sorted([card.rank for card in cards])
    prev_rank = ranks[0]
    for rank in ranks[1:]:
        if rank - prev_rank != 1:
            return False
        prev_rank = rank

    return True

# def parse_deck(deck_string):
