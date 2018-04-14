from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.

from game.forms import DiscardForm, TurnForm
from game.models import RummyGame, RummyPlayer
from game.rummy_utils import *


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

    current_card = deck.pop().card_to_string()
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

    if request.method == 'POST':
        form = TurnForm(request.POST)
        if form.is_valid():
            choice = form.cleaned_data['turn_choices']
            handle_turn_choice(choice, game)
            return HttpResponseRedirect('/game/discard/')
    else:
        form = TurnForm()

    context = dict()
    context['turn'] = game.turn
    context['current_card'] = string_to_card(game.current_card)
    context['hand'] = string_to_deck(game.turn.hand)
    context['turn_options_form'] = form

    return render(request, 'game/turn.html', context)


def discard(request):
    """
    discard card from hand, switch turns when done
    :param request: 
    :return: 
    """
    print('in discard')
    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    hand = string_to_deck(game.turn.hand)
    # for discard_form, discard choices come from current hand. Pairs of cards with (model_value, display_value)
    list_of_cards = [(card.card_to_string(), str(card)) for card in hand]

    if request.method == 'POST':
        form = DiscardForm(list_of_cards=list_of_cards, data=request.POST or None)
        form_is_valid = form.is_valid()
        if form_is_valid:
            print('valid discard post')
            choice = string_to_card(form.cleaned_data['cards'])
            print(f'discard choice: {choice}, type: {type(choice)}')
            game = handle_discard_choice(choice, game)
            if game.turn == game.player1:
                game.turn = game.player2
            elif game.turn == game.player2:
                game.turn = game.player1
            else:
                print('game turn comparison failed')
            game.save()
            print(f'after discard save {game.turn}')
            return HttpResponseRedirect('/game/turn/')
        else:
            print('invalid discard post')
    else:
        form = DiscardForm(list_of_cards=list_of_cards)

    context = dict()
    context['turn'] = game.turn
    context['current_card'] = string_to_card(game.current_card)
    context['hand'] = hand
    context['discard_form'] = form

    return render(request, 'game/discard.html', context)


def handle_discard_choice(discard_card, game):
    """
    remove discard choice from hand, and put on top of deck
    :param discard_card: 
    :param game: 
    :return: 
    """
    print(f'in handle discard, {discard_card}')
    rp = RummyPlayer.objects.get(id=game.turn.id)

    hand = string_to_deck(game.turn.hand)
    hand.remove(discard_card)
    rp.hand = deck_to_string(hand)
    rp.save()

    game.current_card = discard_card.card_to_string()
    game.save()

    return game


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

    elif choice == 'current_card':
        # add current_card to hand
        hand.append(string_to_card(game.current_card))
        rp.hand = deck_to_string(hand)
        rp.save()
        game.turn.hand = rp.hand
        game.current_card = deck.pop().card_to_string()
        game.deck = deck_to_string(deck)
        game.save()

    elif choice == 'declare_gin':
        # determine if hand has gin: all cards in melds

        pass