from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages

from ..models import Venue, Artist, Note, Show, UserDetails
from ..forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm, UserDetailsForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.core.exceptions import ObjectDoesNotExist


def user_profile(request, user_pk):
    # Get user profile for any user on the site
    can_edit = False
    user = User.objects.get(pk=user_pk)
    if user == request.user:
        can_edit = True
    
    try:
        user_details = UserDetails.objects.get(user=user)
    except ObjectDoesNotExist:
        user_details = UserDetails(user=user, display_name='', location='', favorite_genres='', bio='')

    
    usernotes = Note.objects.filter(user=user.pk).order_by('-posted_date')
    return render(request, 'lmn/users/user_profile.html', { 'user_profile': user , 'notes': usernotes, 'user_details': user_details, 'can_edit': can_edit})
    
    
@login_required
def my_user_profile(request):
    # Editable user profile
    logged_in_user = request.user
    
    try:
        user_details = UserDetails(user=logged_in_user)
    except ObjectDoesNotExist:
        user_details = UserDetails(user=logged_in_user, display_name='', location='', favorite_genres='', bio='')
    
    if request.method == 'POST':
        form = UserDetailsForm(request.POST, instance=user_details)

        if form.is_valid():
            try:
                update = form.save(commit=False)
                update.user = logged_in_user
                update.save()
                return redirect('user_profile', user_pk=logged_in_user.pk)
            except Exception as e:
                messages.warning(request, e)
        else:
            messages.add_message(request, messages.ERROR, 'Unable to save data')

    form = UserDetailsForm(instance=user_details)
    return render(request, 'lmn/users/edit_profile.html', {'logged_in_user': logged_in_user, 'user_details': user_details, 'detail_form': form})

def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            user = form.save()
            user = authenticate(username=request.POST['username'], password=request.POST['password1'])
            if user:
                login(request, user)
                return redirect('user_profile', user_pk=request.user.pk)
            else:
                messages.add_message(request, messages.ERROR, 'Unable to log in new user')
        else:
            messages.add_message(request, messages.INFO, 'Please check the data you entered')
            # include the invalid form, which will have error messages added to it. The error messages will be displayed by the template.
            return render(request, 'registration/register.html', {'form': form} )

    form = UserRegistrationForm()
    return render(request, 'registration/register.html', {'form': form} )
