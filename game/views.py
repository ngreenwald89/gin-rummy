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
    hand1 = cards_to_string([deck.pop() for i in range(10)])
    hand2 = cards_to_string([deck.pop() for i in range(10)])
    # hand1 = ','.join([str(deck.pop().as_number()) for i in range(10)])
    # hand2 = ','.join([str(deck.pop().as_number()) for i in range(10)])
    player1.hand = hand1
    player2.hand = hand2
    player1.save()
    player2.save()

    current_card = deck.pop().card_to_string()
    game = RummyGame(player1=player1, player2=player2, turn=player1, deck=cards_to_string(deck))
    game.current_card = current_card
    game.save()
    request.session['game_pk'] = game.pk
    print(game.pk)

    # render function that makes use of the new game.html page created !!

    # return HttpResponse(f"""
    #                         {game.turn}'s turn,
    #                         current showing card: {game.current_card}.
    #                         {game.turn}'s cards: {game.turn.hand}
    #                         """)
    return HttpResponseRedirect('/game/turn/')


def gameover(request):
    """
    redirected here only if player has won (or i guess if we run out of cards?)
    :param request: 
    :return: 
    """
    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)
    context = dict()
    context['winner'] = game.winner
    context['turn'] = game.turn
    context['current_card'] = string_to_card(game.current_card)
    context['hand'] = sort_cards(string_to_cards(game.turn.hand))
    context['melds'] = game.turn.identify_melds()

    return render(request, 'game/gameover.html', context)


def turn(request):
    """
    
    :param request: 
    :return: 
    """

    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    player_does_not_have_gin_message = False

    if request.method == 'POST':
        form = TurnForm(request.POST)
        if form.is_valid():
            choice = form.cleaned_data['turn_choices']
            r = handle_turn_choice(choice, game)
            if choice in ('current_card', 'top_of_deck_card'):
                return HttpResponseRedirect('/game/discard/')
            elif choice == 'declare_gin':
                if r:
                    return HttpResponseRedirect('/game/gameover/')
                else:
                    player_does_not_have_gin_message = True
    else:
        form = TurnForm()

    context = dict()
    context['turn'] = game.turn
    context['current_card'] = string_to_card(game.current_card)
    context['hand'] = sort_cards(string_to_cards(game.turn.hand))
    context['melds'] = game.turn.identify_melds()
    context['turn_options_form'] = form
    context['gin_message'] = player_does_not_have_gin_message

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

    hand = game.turn.string_to_hand()
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
    context['melds'] = game.turn.identify_melds()
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

    hand = string_to_cards(game.turn.hand)
    hand.remove(discard_card)
    rp.hand = cards_to_string(sort_cards(hand))
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


def handle_turn_choice(choice, game):

    rp = RummyPlayer.objects.get(id=game.turn.id)
    hand = game.turn.string_to_hand()
    deck = string_to_cards(game.deck)

    if choice == 'top_of_deck_card':
        # add top of deck_card to hand
        hand.append(deck.pop())
        rp.hand = cards_to_string(sort_cards(hand))
        rp.save()
        game.turn.hand = rp.hand
        game.deck = cards_to_string(deck)
        game.save()

    elif choice == 'current_card':
        # add current_card to hand
        hand.append(string_to_card(game.current_card))
        rp.hand = cards_to_string(sort_cards(hand))
        rp.save()
        game.turn.hand = rp.hand
        game.current_card = deck.pop().card_to_string()
        game.deck = cards_to_string(deck)
        game.save()

    elif choice == 'declare_gin':
        # determine if hand has gin: all cards in melds
        set1 = set([c.as_number() for c in hand])
        set2 = set([card.as_number() for meld in game.turn.identify_melds() for card in meld])
        melds = game.turn.identify_melds()

        if set1 == set2:
            # need additional checks - make sure melds are not overlapping
            # s = set()
            # for meld in melds:
            #     for c in meld:
            #         if c in s:
            #             print('overlap')
            #         s.add(c)

            game.winner = game.turn
            game.save()
            print(f'{game.turn} is the Winner!!')
            return True
        else:
            print(f'{game.turn} is not the winner, keep playing')
            return False
