import requests
import os
import json
from django.http import HttpResponse
from .models import *
import logging

logger = logging.getLogger(__name__)


def find_shows(request):
    # Search Parameters
    root_url = 'https://app.ticketmaster.com/discovery/v2/events'
    ticketmaster_key = os.environ.get('TicketMasterKey')
    show_id = ''
    show_url = f'/{show_id}' # add this to the url to get details on a specific show
    city = 'Minneapolis'
    state = 'mn'
    country = 'US'
    search_radius = '50'
    segment_name = 'music'
    locale = '*'

    # Controls looping over json pagination
    page = 1
    page_size = '20'

    # Initial Query
    query = {'apikey' : ticketmaster_key , 'locale' : locale ,'city': city, 'state': state, 'countryCode': country, 'radius': search_radius, 'segmentName': segment_name, 'size': page_size, 'page' : str(page)}

    try:
        data = requests.get(root_url, params=query).json()            
        # Sets page_count to number of pages listed in api response
        page_count = (data['page']['totalPages'])

        # Loops through each page of the api response
        for current_page in range(2, page_count):
            page = current_page
            query = {'apikey' : ticketmaster_key , 'locale' : locale ,'city': city, 'state': state, 'countryCode': country, 'radius': search_radius, 'segmentName': segment_name, 'size': page_size, 'page' : str(page)}
            data = requests.get(root_url, params=query).json() 
            propogate_db(data)

    except Exception as e: 
        return HttpResponse(f'Error: {e}\nResponse recieved:\n{data}')
    return HttpResponse(f'Data recieved. Total pages {str(page_count)}')

def propogate_db(data):
    for show in data['_embedded']['events']:
        artist = add_artist( show['id'], show['name'] )
        venue = add_venue( show['_embedded']['venues'][0]['id'] , show['_embedded']['venues'][0]['name'] , show['_embedded']['venues'][0]['city']['name'] , show['_embedded']['venues'][0]['state']['stateCode'])
        add_show( show['id'] , show['dates']['start']['dateTime'] , artist , venue )

def add_venue(venue_id, venue_name, venue_city, venue_state):
    created_venue, created = Venue.objects.get_or_create(name = venue_name,  city = venue_city, state = venue_state, api_id=venue_id)
    return created_venue  

def add_artist(artist_id, artist_name):
    created_artist, created = Artist.objects.get_or_create(api_id = artist_id, name = artist_name)
    return created_artist
    

def add_show(show_id, show_date, show_artist, show_venue):
    created_show, created = Show.objects.get_or_create(api_id = show_id, show_date = show_date, artist = show_artist, venue = show_venue)
    return created_show