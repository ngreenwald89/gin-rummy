from django.shortcuts import render
from django.http import HttpResponse, HttpResponseRedirect

from game.forms import TurnForm
from game.models import *
from game.rummy_utils import *
from django.contrib.auth.models import User

# Create your views here.
import random


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
    hand1 = ','.join([str(deck.pop().as_number()) for i in range(10)])
    hand2 = ','.join([str(deck.pop().as_number()) for i in range(10)])
    player1.hand = hand1
    player2.hand = hand2
    player1.save()
    player2.save()

    game = RummyGame(player1=player1, player2=player2, turn=player1, deck=','.join(map(lambda x: str(x.as_number()), deck)))
    game.current_card = str(deck.pop().as_number())
    game.save()
    request.session['game_pk'] = game.pk
    print(game.pk)

    return HttpResponseRedirect('/game/turn/')


def turn(request):
    """
    
    :param request: 
    :return: 
    """

    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    context = dict()
    context['turn'] = game.turn
    context['current_card'] = card_from_number(game.current_card)

    hand = game.turn.hand
    context['hand'] = list(map(card_from_number, hand.split(',')))

    if request.method == 'POST':
        form = TurnForm(request.POST)
        if form.is_valid():
            pass
    else:
        form = TurnForm()

    context['form'] = form

    return render(request, 'game/turn.html', context)


def initialize_deck():
    deck = []
    for suit in ('C', 'S', 'H', 'D'):
        for rank in (1, 2, 3, 4, 5, 6, 7, 8, 9, 10, 11, 12, 13):
            deck.append(Card(suit=suit, rank=rank))

    random.shuffle(deck)

    return deck