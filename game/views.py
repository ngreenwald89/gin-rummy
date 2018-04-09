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

    current_card = str(deck.pop().as_number())
    game = RummyGame(player1=player1, player2=player2, turn=player1, deck=deck_to_string(deck))
    game.current_card = current_card
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
    context['current_card'] = string_to_card(game.current_card)

    hand = game.turn.hand
    context['hand'] = string_to_deck(hand)

    if request.method == 'POST':
        form = TurnForm(request.POST)
        if form.is_valid():
            choice = form.cleaned_data['turn_choices']
            print('the choice', choice)
            game = handle_turn_choice(choice, game)
            context['hand'] = string_to_deck(game.turn.hand)
            context['current_card'] = string_to_card(game.current_card)
            return render(request, 'game/turn.html', context)
            # after choice, must force discard
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


def string_to_deck(card_string):
    """
    convert deck field in from db string to list of Card objects
    :param card_string: n1,n2, ...
    :return: [Card1, Card2, ...]
    """
    return list(map(string_to_card, card_string.split(',')))


def deck_to_string(deck):
    """
    convert list of Card objects to string for db deck field
    :param deck: 
    :return: 
    """
    return ','.join(map(lambda x: str(x.as_number()), deck))


def handle_turn_choice(choice, game):

    rp = RummyPlayer.objects.get(id=game.turn.id)
    hand = string_to_deck(game.turn.hand)
    deck = string_to_deck(game.deck)

    if choice == 'top_of_deck_card':
        # add top of deck_card to hand
        hand.append(deck.pop())
        rp.hand = deck_to_string(hand)
        rp.save()
        game.turn.hand = rp.hand
        game.deck = deck_to_string(deck)
        game.save()
    else:
        # add current_card to hand
        hand.append(string_to_card(game.current_card))
        rp.hand = deck_to_string(hand)
        rp.save()
        game.turn.hand = rp.hand
        game.current_card = str(deck.pop().as_number())
        game.save()

    return game