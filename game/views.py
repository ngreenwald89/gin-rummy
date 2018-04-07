from django.shortcuts import render
from django.http import HttpResponse

from game.models import Deck, Player
# Create your views here.
import random

def start(request):
    d = Deck()
    p1 = Player('Nat')
    p2 = Player('Murtuza')
    for i in range(10):
        p1.hand.append(d.deal())
        p2.hand.append(d.deal())

    first_card = d.deal()
    first_turn = random.choice([p1, p2])


    return HttpResponse(f"{first_turn}'s turn, face card: {first_card}")




