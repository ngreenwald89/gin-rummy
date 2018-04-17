from django.contrib.auth.models import User
from django.http import HttpResponseRedirect
from django.shortcuts import render

# Create your views here.

from game.forms import DiscardForm, MeldForm, DrawForm, PlayMeldForm, ChooseMeldForm
from game.models import RummyGame, RummyPlayer, GameLog
from game.rummy_utils import *


def start(request):
    """
    this starts a game, initializing a deck, adding players to a game, dealing them cards, and starting a turn.
    
    at the moment, it statically picks two players from the User table
    it needs to be configured to pick the player who has just signed in
    :param request: 
    :return: 
    """
    deck = initialize_deck()

    users = User.objects.all()
    player1 = RummyPlayer(user=users[0])
    player2 = RummyPlayer(user=users[1])
    hand1 = cards_to_string([deck.pop() for i in range(10)])
    hand2 = cards_to_string([deck.pop() for i in range(10)])
    player1.hand = hand1
    player2.hand = hand2
    player1.save()
    player2.save()

    current_card = deck.pop().card_to_string()
    # first turn should be randomized
    first_turn = random.choice([player1, player2])
    game = RummyGame(player1=player1, player2=player2, turn=first_turn, deck=cards_to_string(deck))
    game.current_card = current_card
    game.save()
    game_log = GameLog(game=game)
    game_log.save()
    request.session['game_pk'] = game.pk
    print(game.pk)

    return HttpResponseRedirect('/game/draw/')


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

    return render(request, 'game/gameover.html', context)


def draw(request):
    """
    https://www.thespruce.com/rummy-card-game-rules-and-strategies-411141
    On each turn, players must follow this sequence:

        (1) Draw one card, either from the top of the draw pile or the top of the discard pile.
        
        (2) The player may (but does not have to) play a meld of cards (see "Melds" below) or add to another player's meld (see "Laying Off" below).
        
        (3) The player must discard one card, adding it (face up) to the top of the discard pile.
    :param request: 
    :return: 
    """

    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    invalid_message = None

    if request.method == 'POST':
        form = DrawForm(request.POST)
        if form.is_valid():
            choice = form.cleaned_data['draw_choices']
            handle_draw_choice(choice, game)
            return HttpResponseRedirect('/game/meld_options/')
        else:
            invalid_message = 'Invalid Draw Option'
    else:
        form = DrawForm()

    context = default_turn_context(game, form, invalid_message)

    return render(request, 'game/draw.html', context)


def meld_options(request):
    """
    (2) The player may (but does not have to) play a meld of cards (see "Melds" below) or add to another player's meld (see "Laying Off" below).
    :param request: 
    :return: 
    """
    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    invalid_message = None

    if request.method == 'POST':
        form = MeldForm(request.POST)
        if form.is_valid():
            choice = form.cleaned_data['meld_choices']
            if choice == 'play_meld':
                return HttpResponseRedirect('/game/play_meld/')
            elif choice == 'lay_off':
                return HttpResponseRedirect('/game/lay_off/')
            elif choice == 'continue_to_discard':
                return HttpResponseRedirect('/game/discard/')
        else:
            print('invalid form')
            invalid_message = 'Invalid Choice'
    else:
        form = MeldForm()

    context = default_turn_context(game, form, invalid_message)

    return render(request, 'game/meld_options.html', context)


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

    invalid_message = None

    if request.method == 'POST':
        form = DiscardForm(list_of_cards=list_of_cards, data=request.POST or None)
        form_is_valid = form.is_valid()
        if form_is_valid:
            print('valid discard post')
            choice = string_to_card(form.cleaned_data['cards'])
            print(f'discard choice: {choice}')
            game = handle_discard_choice(choice, game)
            # switch turns
            if game.turn == game.player1:
                game.turn = game.player2
            elif game.turn == game.player2:
                game.turn = game.player1
            else:
                print('game turn comparison failed')
            game.save()
            print(f'after discard save {game.turn}')
            return HttpResponseRedirect('/game/draw/')
        else:
            print('invalid discard post')
            invalid_message = 'Invalid Discard Choice'
    else:
        form = DiscardForm(list_of_cards=list_of_cards)

    context = default_turn_context(game, form, invalid_message)

    return render(request, 'game/discard.html', context)


def handle_discard_choice(discard_card, game):
    """
    remove discard choice from hand, and put on top of deck
    :param discard_card: card from hand to be discarded
    :param game: RummyGame object from database that keeps state of game
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


def handle_draw_choice(choice, game):

    rp = RummyPlayer.objects.get(id=game.turn.id)
    hand = game.turn.string_to_hand()
    deck = string_to_cards(game.deck)
    game_log = GameLog.objects.get(game=game)

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


def play_meld(request):
    """
    # allow player to select multiple cards from hand
    # if a valid meld, play the meld and move one to discard
    # if not, say it's invalid and repeat meld choices
    :param request: 
    :return: 
    """

    print('in play_meld')
    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    hand = game.turn.string_to_hand()
    # for play_meld_form, meld choices come from current hand. Pairs of cards with (model_value, display_value)
    list_of_cards = [(card.card_to_string(), str(card)) for card in hand]
    invalid_message = None

    if request.method == 'POST':
        form = PlayMeldForm(list_of_cards=list_of_cards, data=request.POST or None)
        if form.is_valid():
            print('valid play_meld post')
            print(form.cleaned_data['cards'])  # returns list of cards as number values: ['45', '46', '47'] for 6,7,8 of Spades
            selected_cards = list(map(string_to_card, form.cleaned_data['cards']))
            if validate_meld(selected_cards):

                # 1. remove cards from hand
                for c in selected_cards:
                    hand.remove(c)

                rp = RummyPlayer.objects.get(id=game.turn.id)
                rp.hand = cards_to_string(hand)
                rp.save()

                # 2. add cards to melds
                game.turn.hand = rp.hand
                meld = cards_to_string(selected_cards)
                game.append_meld(meld)
                game.save()

            else:
                # if selected cards invalid, reload meld_options page
                return HttpResponseRedirect('/game/meld_options/')

            return HttpResponseRedirect('/game/discard/')

        else:
            invalid_message = 'invalid play_meld Choice'

    else:
        form = PlayMeldForm(list_of_cards=list_of_cards)

    context = default_turn_context(game, form, invalid_message)

    return render(request, 'game/play_meld.html', context)


def lay_off(request):
    """
    player will select cards to play on a meld
        must select meld on board to play on
        then select cards to play from his hand
    :param request: 
    :return: 
    """
    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    hand = game.turn.string_to_hand()
    melds = game.meld_string_to_melds()
    # melds = [[card1, card2, card3], [card5, card6, card7]]
    # melds for form should be list of melds, each meld one string of cards
    list_of_melds = []
    for meld in melds:
        meld_string = ', '.join(str(card) for card in meld)
        meld_nums = ','.join(card.card_to_string() for card in meld)
        list_of_melds.append((meld_nums, meld_string))
    list_of_cards = [(card.card_to_string(), str(card)) for card in hand]

    if request.method == 'POST':
        form = ChooseMeldForm(list_of_melds=list_of_melds, list_of_cards=list_of_cards, data=request.POST or None)
        if form.is_valid():
            selected_meld = string_to_cards(form.cleaned_data['melds'])
            selected_cards = list(map(string_to_card, form.cleaned_data['cards']))
            lay_off = selected_meld + selected_cards

            if validate_meld(lay_off):

                # 1. remove cards from hand
                for c in selected_cards:
                    hand.remove(c)

                rp = RummyPlayer.objects.get(id=game.turn.id)
                rp.hand = cards_to_string(hand)
                rp.save()

                # 2. add cards to melds
                game.turn.hand = rp.hand
                game.remove_meld(form.cleaned_data['melds'])
                new_meld = cards_to_string(lay_off)
                game.append_meld(new_meld)
                game.save()

                return HttpResponseRedirect('/game/discard/')

            else:
                # if selected cards invalid, reload play_meld page
                print(f'invalid_meld: {lay_off}')
                return HttpResponseRedirect('/game/meld_options/')

    else:
        form = ChooseMeldForm(list_of_melds=list_of_melds, list_of_cards=list_of_cards)

    context = default_turn_context(game, form)

    return render(request, 'game/lay_off.html', context)


def default_turn_context(game, form=None, invalid_message=None):

    context = dict()
    context['turn'] = game.turn
    context['current_card'] = string_to_card(game.current_card)
    context['hand'] = sort_cards(game.turn.string_to_hand())
    context['possible_melds'] = game.turn.identify_melds()
    context['played_melds'] = game.meld_string_to_melds()
    context['gameplay_form'] = form

    if invalid_message:
        context['invalid_message'] = invalid_message

    return context
