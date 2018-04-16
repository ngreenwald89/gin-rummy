from django import forms


class DrawForm(forms.Form):

    CHOICES = [('current_card', 'current_card'), ('top_of_deck_card', 'top_of_deck_card')]
    draw_choices = forms.ChoiceField(choices=CHOICES, label='draw_choices')


class MeldForm(forms.Form):

    CHOICES = [('play_meld', 'play_meld'), ('lay_off', 'lay_off'), ('continue_to_discard', 'continue_to_discard')]
    meld_choices = forms.ChoiceField(choices=CHOICES, label='meld_choices')


class DiscardForm(forms.Form):

    def __init__(self, list_of_cards, *args, **kwargs):
        super(DiscardForm, self).__init__(*args, **kwargs)
        CHOICES = [(c[0], c[1]) for c in list_of_cards]
        self.fields['cards'] = forms.ChoiceField(choices=CHOICES, label='card_choices')


class PlayMeldForm(forms.Form):

    def __init__(self, list_of_cards, *args, **kwargs):
        super(PlayMeldForm, self).__init__(*args, **kwargs)
        CHOICES = [(c[0], c[1]) for c in list_of_cards]
        self.fields['cards'] = forms.MultipleChoiceField(choices=CHOICES, label='card_choices')


class ChooseMeldForm(forms.Form):

    def __init__(self, list_of_melds, list_of_cards, *args, **kwargs):
        super(ChooseMeldForm, self).__init__(*args, **kwargs)
        MELD_CHOICES = [(m[0], m[1]) for m in list_of_melds]
        CARD_CHOICES = [(c[0], c[1]) for c in list_of_cards]
        self.fields['melds'] = forms.ChoiceField(choices=MELD_CHOICES, label='meld_choices')
        self.fields['cards'] = forms.MultipleChoiceField(choices=CARD_CHOICES, label='card_choices')