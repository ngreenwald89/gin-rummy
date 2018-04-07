from django import forms
from django.contrib.auth.models import User


class UserForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput())

    class Meta():
        model = User
        fields = ('username', 'email', 'password')


# class UserProfileModelForm(forms.ModelForm):
#     class Meta():
#         model = UserProfileModel
#         # fields = ('portfolio_site','profile_pic')
