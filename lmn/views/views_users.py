from django.shortcuts import render, redirect
from django.contrib import messages

from ..models import Venue, Artist, Note, Show, Profile
from ..forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm, ProfileForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

""" All of the users information """


def user_profile(request, user_pk):
    """ Get the user profile for any user on the site """
    user = User.objects.get(pk=user_pk)
    usernotes = Note.objects.filter(user=user.pk).order_by('-posted_date')
    return render(request, 'lmn/users/user_profile.html', { 'user_profile': user , 'notes': usernotes })


@login_required
def my_user_profile(request):
    """ Gather information on the user that is signed in """
    if request.method == 'POST':
        form = ProfileForm(request.POST, instance=request.user.profile) if hasattr(request.user, 'profile') else  ProfileForm(request.POST)
        if form.is_valid():
            profile_form = form.save(commit=False)
            profile_form.user = request.user
            profile_form.save()

    user = request.user
    usernotes = Note.objects.filter(user=user.pk).order_by('-posted_date')
    form = ProfileForm(instance=user.profile) if hasattr(user, 'profile') else ProfileForm()
    data = {
        'user_profile': user,
        'notes': usernotes,
        'form': form,
    }

    return render(request, 'lmn/users/my_user_profile.html', data)


def register(request):
    """ Method based on registring the users """
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            if user:
                login(request, user)
                return redirect('user_profile', user_pk=request.user.pk)
            elif user:
                logout(request, user)
                return redirect('registration/logout.html')
            else:
                messages.add_message(request, messages.ERROR, 'Unable to log in new user')
        else:
            messages.add_message(request, messages.INFO, 'Please check the data you entered')
            # include the invalid form, which will have error messages added to it. The error messages will be displayed by the template.
            return render(request, 'registration/register.html', {'form': form} )

    


    form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form} )

def goodbye_message(request):
        """ Send the user to the goodbye message page after signing out """
        return render(request, 'registration/goodbye.html')




