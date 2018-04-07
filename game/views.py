from django.shortcuts import render
from django.http import HttpResponse

from game.models import *
from game.rummy_utils import *
from django.contrib.auth.models import User

# Create your views here.
import random


def start1(request):
    """
    old way - does not use Django classes
    :param request: 
    :return: 
    """
    p1 = Player('Nat')
    p2 = Player('Murtuza')
    game = Game(p1, p2)
    if game.turn == p1:
        current_hand = game.player1.hand
    else:
        current_hand = game.player2.hand

    return HttpResponse(f"""
                        {game.turn}'s turn, 
                        current showing card: {game.current_card}. 
                        {game.turn}'s cards: {current_hand}
                        """)


def start(request):
    """
    being used - has django classes
    :param request: 
    :return: 
    """
    deck = initialize_deck()

    users = User.objects.all()
    player1 = RummyPlayer(user=users[0])
    player2 = RummyPlayer(user=users[1])
    hand1 = [deck.pop() for i in range(10)]
    hand2 = [deck.pop() for i in range(10)]
    player1.hand = hand1
    player2.hand = hand2

    game = RummyGame(player1=player1, player2=player2, turn=player1)
    game.current_card = deck.pop()

    return HttpResponse(f"""
                            {game.turn}'s turn, 
                            current showing card: {game.current_card}. 
                            {game.turn}'s cards: {game.turn.hand}
                            """)


def game(request):

    if request.method == 'POST':
        pass
    else:


def start_game_deal(deck, player1, player2):
    """
    distribute cards to players at start of game
    :return: 
    """
    for i in range(10):
        player1.hand.append(deck.pop())
        player2.hand.append(deck.pop())


def initialize_deck():
    deck = []
    for suit in ('Clubs', 'Spades', 'Hearts', 'Diamonds'):
        for rank in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
            deck.append(Card(suit=suit, rank=rank))

    random.shuffle(deck)

    return deck