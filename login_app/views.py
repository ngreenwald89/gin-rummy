from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
# ,UserProfileModelForm
from django.http import HttpResponseRedirect, HttpResponse
from django.shortcuts import render
from django.urls import reverse

from game.views import reset_token
from login_app.forms import UserForm


# Create your views here.

def home(request):
    return render(request, 'login_app/home.html')


@login_required
def user_logout(request):

    reset_token(request)
    logout(request)
    # Return to homepage.
    return HttpResponseRedirect(reverse('home'))


def register(request):

    registered = False

    if request.method == 'POST':

        user_form = UserForm(data=request.POST)

        if user_form.is_valid():

            # Save User Form to Database
            user = user_form.save()

            # Hash the password
            user.set_password(user.password)

            # Update with Hashed password
            user.save()

            # Registration Successful!
            registered = True

        else:
            # One of the forms was invalid if this else gets called.
            print(user_form.errors)

    else:
        # Was not an HTTP post so we just render the forms as blank.
        user_form = UserForm()
        # profile_form = UserProfileModelForm()

    # This is the render and context dictionary to feed
    # back to the registration.html file page.
    context = {'user_form': user_form, 'registered': registered}
    return render(request, 'login_app/registration.html', context)


def user_login(request):

    if request.method == 'POST':
        # Get : username and password
        username = request.POST.get('username')
        password = request.POST.get('password')

        # built-in auth function:
        user = authenticate(username=username, password=password)

        # If user is present !
        if user:
            # If the user is active
            if user.is_active:
                # Log the user in.
                login(request, user)
                # Send the user to their game page.

                return HttpResponseRedirect('/game/start')

            else:
                # If account is not active:
                return HttpResponse("Your account is not active.")
        else:
            print("Someone tried to login and failed.")
            print("They used username: {} and password: {}".format(username, password))
            return HttpResponse("Invalid login entered")

    else:
        # username or password are empty, redirect to the same page to retry.
        return render(request, 'login_app/login.html', {})
