from django import template

from game import rummy_utils

register = template.Library()


@register.simple_tag
def string_to_card(card_string):
    return rummy_utils.string_to_card(card_string)

@register.simple_tag
def string_to_cards(cards_string):
    # when you fix lay_off saving - get rid of try / except
    try:
        return rummy_utils.string_to_cards(cards_string)
    except Exception as e:
        return 'error string'