from django.shortcuts import render
from django.http import HttpResponse

from game.models import Deck, Player, Game
# Create your views here.
import random

def start(request):
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




