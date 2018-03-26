from django.conf.urls import url

from login_app import views

# SET THE NAMESPACE!
app_name = 'login_app'

# Be careful setting the name to just /login use userlogin instead!
urlpatterns=[
    url('^register/$',views.register,name='register'),
    url('^user_login/$',views.user_login,name='user_login'),
]
