from django.shortcuts import render, redirect, get_object_or_404

from ..models import Venue, Artist, Note, Show
from ..forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

from django.core.paginator import Paginator

""" All the information about venues """

def venue_list(request):
    """ Get all the Venues in a list """
    form = VenueSearchForm()
    search_name = request.GET.get('search_name')

    if search_name:
        #search for this venue, display results
        venues = Venue.objects.filter(name__icontains=search_name).order_by('name')
    else :
        venues = Venue.objects.all().order_by('name') # Get all the venues from database

    venue_paginator = Paginator(venues, 3) # 2 Per page as of right now

    page_num = request.GET.get('page') # Get the page number based on where you are in the list fromt the URL

    page_of_venues = venue_paginator.get_page(page_num) 

    return render(request, 'lmn/venues/venue_list.html', { 'venues': page_of_venues, 'form': form, 'search_term': search_name })


def artists_at_venue(request, venue_pk):   # pk = venue_pk
    """ Get all of the artists who have played a show at the venue with pk provided """

    shows = Show.objects.filter(venue=venue_pk).order_by('-show_date') 
    venue = Venue.objects.get(pk=venue_pk)

    return render(request, 'lmn/artists/artist_list_for_venue.html', { 'venue': venue, 'shows': shows })


def venue_detail(request, venue_pk):
    """ Get all the information on a venue """
    venue = get_object_or_404(Venue, pk=venue_pk)
    return render(request, 'lmn/venues/venue_detail.html' , { 'venue': venue })
