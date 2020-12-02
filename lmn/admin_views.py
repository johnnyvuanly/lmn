import requests, os
from .models import Venue, Artist, Show
from django.http import HttpResponse
from django.db import IntegrityError
from django.shortcuts import render, redirect, get_object_or_404

key = os.environ.get('TICKETMASTER_KEY')

def get_data(request):
    
    url ='https://app.ticketmaster.com/discovery/v2/events'
    query = {'classificationName': 'music','stateCode' : 'MN' , 'page' : 4 , 'apikey' : key}
    data = requests.get(url, params=query).json()
    # finds how many results so it can iterate the correct amount of times
    events = data['_embedded']['events']
    event_count = len(events)

    for x in range(event_count):
        # VENUE DATA
        venue_name = data['_embedded']['events'][x]['_embedded']['venues'][0]['name']
        venue_state = data['_embedded']['events'][x]['_embedded']['venues'][0]['state']['stateCode']
        venue_city = data['_embedded']['events'][x]['_embedded']['venues'][0]['city']['name']
        # ARTIST DATA
        artist = data['_embedded']['events'][x]['_embedded']['attractions'][0]['name']
        # SHOW DATA 
        ## date and time separated for new model
        show_date = data['_embedded']['events'][x]['dates']['start']['localDate']
        show_time = data['_embedded']['events'][x]['dates']['start']['localTime']

        try:
            # Checking to see if venue exists
            if Venue.objects.filter(name=venue_name).exists():
                # grabs venue object if exists for show info
                venue_object = Venue.objects.filter(name=venue_name).get()  
            else:
                venue_object = Venue(name=venue_name, city=venue_city, state=venue_state)
                venue_object.save()
            # If artist exists it won't try to add a duplicate
            if Artist.objects.filter(name=artist).exists():
                artist_object = Artist.objects.filter(name=artist).get()
            else:
                artist_object = Artist(name=artist)
                artist_object.save()
            #
            if Show.objects.filter(show_date=show_date, show_time=show_time, artist=artist_object,venue=venue_object).exists():
                #ok
                pass
            else:
                show_object = Show(show_date=show_date, show_time=show_time, artist=artist_object,venue=venue_object)
                show_object.save()
            
        except IntegrityError:
            return HttpResponse('AHHHH')
    # returns to homepage
    return render(request, 'lmn/home.html')
