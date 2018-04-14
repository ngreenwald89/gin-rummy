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
        if all([type(rank) == int, rank > 0, rank < 14]):
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

    def __eq__(self, other):
        return self.as_number() == other.as_number()


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


def validate_meld(cards):
    """

    :param cards: list of Card objects
    :return: Boolean
    """
    return validate_same_rank(cards) or validate_run(cards)


def validate_same_rank(cards):
    """
    validate 3 of a kind or 4 of a kind
    :param cards: list of Card objects
    :return: Boolean
    """
    if len(cards) not in (3, 4):
        return False
    return all(card.rank == cards[0].rank for card in cards)


def validate_run(cards):
    """
    a run is 3 to 10 consecutive cards of the same suit
    :param cards: list of Card objects
    :return: Boolean 
    """
    if len(cards) < 3 or len(cards) > 10:
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


def identify_melds(hand):
    """
    determine melds in a hand
    :param hand: list of Card objects
    :return: list of melds, which are lists of Cards
    """
    # determine runs
    clubs = sorted([c for c in hand if c.suit == 'C'], key=lambda x: x.rank)
    diamonds = sorted([c for c in hand if c.suit == 'D'], key=lambda x: x.rank)
    hearts = sorted([c for c in hand if c.suit == 'H'], key=lambda x: x.rank)
    spades = sorted([c for c in hand if c.suit == 'S'], key=lambda x: x.rank)

    # runs
    club_runs = identify_runs(clubs)
    diamond_runs = identify_runs(diamonds)
    heart_runs = identify_runs(hearts)
    spade_runs = identify_runs(spades)

    runs = club_runs + diamond_runs + heart_runs + spade_runs

    print(f'hand: {hand}')
    for run in runs:
        print(f'run: {run}')

    sets = identify_sets(hand)
    for s in sets:
        print(f'set: {s}')

    return runs + sets


def identify_runs(cards):
    run = []
    runs = [run]
    expect = None
    for card in cards:
        if (card.rank == expect) or (expect is None):
            run.append(card)
        else:
            run = [card]
            runs.append(run)
        expect = card.rank + 1

    return list(filter(lambda run: len(run) >= 3, runs))


def identify_sets(cards):
    sets = []
    for i in range(1, 14):
        same_rank = list(filter(lambda x: x.rank == i, cards))
        if len(same_rank) in (3, 4):
            sets.append(same_rank)

    return sets


def string_to_cards(card_string):
    """
    convert deck field in from db string to list of Card objects
    :param card_string: n1,n2, ...
    :return: [Card1, Card2, ...]
    """
    return list(map(string_to_card, card_string.split(',')))


def cards_to_string(cards):
    """
    convert list of Card objects to string for db deck field
    :param cards: 
    :return: 
    """
    return ','.join(map(lambda x: str(x.as_number()), cards))


if __name__ == '__main__':
    d = Deck()
    hand = []
    for i in range(10):
        hand.append(d.deck.pop())

    identify_melds(hand)

