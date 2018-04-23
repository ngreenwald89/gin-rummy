from django.conf.urls import url

from game import views

# SET THE NAMESPACE!
app_name = 'game'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns = [
    url('^start/$', views.start, name='start'),
    url('^startgame/$', views.startgame, name='startgame'),
    url('^draw/$', views.draw, name='draw'),
    url('^meld_options/$', views.meld_options, name='meld_options'),
    url('^play_meld/$', views.play_meld, name='play_meld'),
    url('^lay_off/$', views.lay_off, name='lay_off'),
    url('^discard/$', views.discard, name='discard'),
    url('^gameover/$', views.gameover, name='gameover'),

]
