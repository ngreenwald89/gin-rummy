import logging
import time

from django.contrib.auth.models import User
from django.db.models import Max
from django.http import HttpResponseRedirect
from django.shortcuts import render

from game.forms import DiscardForm, MeldForm, DrawForm, PlayMeldForm, ChooseMeldForm
from game.models import RummyGame, RummyPlayer, Token, GameLog, PlayerStats
from game.rummy_utils import *

# Create your views here.

# Get an instance of a logger
logger = logging.getLogger('gin_rummy')


def start(request):
    """
    being used - has django classes
    :param request: 
    :return: 
    """

    sleep_time_sec = 5

    logger.info('User id : %s', request.user.id)

    tokensCount = len(Token.objects.all())

    if tokensCount < 50:
        logger.info('The tokens were not found, creating 50 tokens - to allow for 50 simultaneous games')
        for idx in range(50):
            token = Token(state=0)
            token.save()

    tokens = Token.objects.all()

    for token in tokens:
        logger.info("Token id being picked is: %s and the token state is: %s ", token.id, token.state)
        request.session['token_id'] = token.id

        if token.state == 0:
            token.state = 1
            token.user0 = request.user.username
            token.save()
            time.sleep(sleep_time_sec)
            token = Token.objects.get(pk=token.id)

            if token.state == 2:
                logger.info('A valid user, with user id: %s, was found waiting, joining the game with him', token.user1)
                request.session['game_pk'] = token.id
                request.session['user0'] = request.user.username
                request.session['user1'] = token.user1
                return HttpResponseRedirect('/game/draw/')
            else:
                logger.info('No valid user found, even after waiting for %s secs; throwing an error', sleep_time_sec)

                reset_token(request)
                context = dict()
                context['sleep_time_sec'] = sleep_time_sec
                return render(request, 'game/game_error.html',context)

        elif token.state == 1:
            # logger.info('A valid user, with user id: %s, was found waiting, joining the game with him', token.user0)
            token.user1 = request.user.username
            token.state = 2
            token.save()

            request.session['game_pk'] = token.id
            request.session['user0'] = token.user0
            request.session['user1'] = request.user.username
            return HttpResponseRedirect('/game/startgame/')
        else:
            continue


def startgame(request):
    """

    :param request:
    :return:

    Logic that creates the game objects, associates them to the same token and starts the game

    """
    deck = initialize_deck()

    player1 = RummyPlayer(user=User.objects.get(username=request.session['user0']))
    player2 = RummyPlayer(user=User.objects.get(username=request.session['user1']))

    hand1 = cards_to_string([deck.pop() for i in range(10)])
    hand2 = cards_to_string([deck.pop() for i in range(10)])
    player1.hand = hand1
    player2.hand = hand2
    player1.save()
    player2.save()

    current_card = deck.pop().card_to_string()
    # first turn should be randomized
    first_turn = random.choice([player1, player2])
    game = RummyGame(id=request.session['game_pk'],
                     player1=player1,
                     player2=player2,
                     turn=first_turn,
                     deck=cards_to_string(deck)
                     )
    game.current_card = current_card
    game.save()

    # Commented to check the functionality with token
    request.session['game_pk'] = game.pk

    logger.info("Game started with the game ID: %s ", game.pk)
    return HttpResponseRedirect('/game/draw/')


def gameover(request):
    """
    redirected here only if player has won (or i guess if we run out of cards?)
    :param request: 
    :return: 
    """

    reset_token(request)

    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    context = default_turn_context(game)
    context['winner'] = game.winner
    context['loser'] = game.loser

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

            game_logs = GameLog.objects.filter(game=game, turn=game.turn)
            if game_logs:

                # get max move_number for game and turn combo for GameLog, increment by 1
                max_move = game_logs.aggregate(Max('move_number'))['move_number__max']
                game_log = GameLog(game=game, turn=game.turn, move_number=(max_move + 1))
            else:
                # first move of the game
                game_log = GameLog(game=game, turn=game.turn, move_number=1)
            game_log.save()

            choice = form.cleaned_data['draw_choices']
            handle_draw_choice(choice, game, game_log)
            return HttpResponseRedirect('/game/meld_options/')
        else:
            invalid_message = 'Invalid Draw Option'
    else:
        form = DrawForm()

    context = default_turn_context(game, form, invalid_message)

    return render(request, 'game/draw.html', context)


def handle_draw_choice(choice, game, game_log):

    rp = RummyPlayer.objects.get(id=game.turn.id)
    hand = game.turn.string_to_hand()
    deck = string_to_cards(game.deck)
    # how to get move number?
    game_log.draw_option = choice

    if choice == 'top_of_deck_card':
        # add top of deck_card to hand
        card = deck.pop()
        hand.append(card)
        rp.hand = cards_to_string(sort_cards(hand))
        rp.save()
        game.turn.hand = rp.hand
        game.deck = cards_to_string(deck)

    elif choice == 'current_card':
        # add current_card to hand
        card = string_to_card(game.current_card)
        hand.append(card)
        rp.hand = cards_to_string(sort_cards(hand))
        rp.save()
        game.turn.hand = rp.hand
        game.current_card = deck.pop().card_to_string()
        game.deck = cards_to_string(deck)

    game.save()
    game_log.draw_card = card.card_to_string()
    game_log.save()


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
            game_log = GameLog.objects.filter(game=game, turn=game.turn).latest('move_number')
            game_log.meld_option = choice
            game_log.save()

            if choice == 'play_meld':
                return HttpResponseRedirect('/game/play_meld/')
            elif choice == 'lay_off':
                return HttpResponseRedirect('/game/lay_off/')
            elif choice == 'continue_to_discard':
                return HttpResponseRedirect('/game/discard/')
        else:
            invalid_message = 'Invalid Choice'
            logger.info('invalid form')
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
    logger.info('in discard')
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

            logger.debug('valid discard post')
            choice = string_to_card(form.cleaned_data['cards'])
            print(f'discard choice: {choice}')
            game = handle_discard_choice(choice, game)

            print(game.turn.string_to_hand())

            if not game.turn.hand:
                game.winner = game.turn
                if game.turn == game.player1:
                    game.loser = game.player2
                else:
                    game.loser = game.player1
                game.save()
                stats = PlayerStats(game=game, winner=game.winner, loser=game.loser)
                stats.save()
                return HttpResponseRedirect('/game/gameover/')

            # switch turns
            if game.turn == game.player1:
                game.turn = game.player2
            elif game.turn == game.player2:
                game.turn = game.player1
            else:
                logger.info('game turn comparison failed')
            game.save()
            logger.info(f'after discard save {game.turn}')
            return HttpResponseRedirect('/game/draw/')
        else:
            logger.debug('invalid discard post')
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
    logger.debug(f'in handle discard, {discard_card}')
    rp = RummyPlayer.objects.get(id=game.turn.id)

    hand = string_to_cards(game.turn.hand)
    hand.remove(discard_card)
    rp.hand = cards_to_string(sort_cards(hand))
    rp.save()
    game.turn.hand = rp.hand

    game.current_card = discard_card.card_to_string()
    game.save()

    game_log = GameLog.objects.filter(game=game, turn=game.turn).latest('move_number')
    game_log.discard_card = discard_card.card_to_string()
    game_log.save()

    return game


def play_meld(request):
    """
    # allow player to select multiple cards from hand
    # if a valid meld, play the meld and move one to discard
    # if not, say it's invalid and repeat meld choices
    :param request:
    :return:
    """

    logger.debug('in play_meld')
    game_pk = request.session.get('game_pk')
    game = RummyGame.objects.get(pk=game_pk)

    hand = game.turn.string_to_hand()
    # for play_meld_form, meld choices come from current hand. Pairs of cards with (model_value, display_value)
    list_of_cards = [(card.card_to_string(), str(card)) for card in hand]
    invalid_message = None

    if request.method == 'POST':
        form = PlayMeldForm(list_of_cards=list_of_cards, data=request.POST or None)
        if form.is_valid():
            logger.info('valid play_meld post')
            logger.info(form.cleaned_data['cards'])  # returns list of cards as number values: ['45', '46', '47'] for 6,7,8 of Spades
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

                game_log = GameLog.objects.filter(game=game, turn=game.turn).latest('move_number')
                game_log.meld_cards = meld
                game_log.save()

                if not game.turn.hand:
                    game.winner = game.turn
                    if game.turn == game.player1:
                        game.loser = game.player2
                    else:
                        game.loser = game.player1
                    game.save()

                    stats = PlayerStats(game=game, winner=game.winner, loser=game.loser)
                    stats.save()
                    return HttpResponseRedirect('/game/gameover/')

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

                game_log = GameLog.objects.filter(game=game, turn=game.turn).latest('move_number')
                game_log.meld_cards = form.cleaned_data['cards']
                game_log.save()

                if not game.turn.hand:
                    game.winner = game.turn
                    if game.turn == game.player1:
                        game.loser = game.player2
                    else:
                        game.loser = game.player1
                    game.save()

                    stats = PlayerStats(game=game, winner=game.winner, loser=game.loser)
                    stats.save()
                    return HttpResponseRedirect('/game/gameover/')

                return HttpResponseRedirect('/game/discard/')

            else:
                # if selected cards invalid, reload play_meld page
                logger.info(f'invalid_meld: {lay_off}')

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


def reset_token(request):
    token_id = request.session['token_id']
    token = Token.objects.get(pk=token_id)

    token.state = 0
    token.user0 = ""
    token.user1 = ""
    token.save()


