from django.conf.urls import url

from game import views

# SET THE NAMESPACE!
app_name = 'game'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns = [
    url('^start/$', views.start, name='start'),
    url('^turn/$', views.turn, name='turn'),
    url('^discard/$', views.discard, name='discard'),
]
