from django import template

from game import rummy_utils

register = template.Library()


@register.simple_tag
def string_to_card(card_string):
    return rummy_utils.string_to_card(card_string)

@register.simple_tag
def string_to_cards(cards_string):
    return rummy_utils.string_to_cards(cards_string)