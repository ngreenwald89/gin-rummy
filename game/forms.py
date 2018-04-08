from django import forms


class TurnForm(forms.Form):

    CHOICES = [('current_card', 'current_card'), ('top_of_deck_card', 'top_of_deck_card')]
    turn_choices = forms.ChoiceField(choices=CHOICES, label='turn_choices')