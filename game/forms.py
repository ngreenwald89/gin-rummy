from django import forms
from game.models import RummyPlayer


class TurnForm(forms.Form):

    CHOICES = [('current_card', 'current_card'), ('top_of_deck_card', 'top_of_deck_card')]
    turn_choices = forms.ChoiceField(choices=CHOICES, label='turn_choices')


class DiscardForm(forms.Form):

    def __init__(self, list_of_cards, *args, **kwargs):
        super(DiscardForm, self).__init__(*args, **kwargs)
        CHOICES = [(c[0], c[1]) for c in list_of_cards]
        self.fields['cards'] = forms.ChoiceField(choices=CHOICES, label='card_choices')