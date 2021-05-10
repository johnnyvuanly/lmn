import requests
import os
import json
from django.http import HttpResponse
from .models import *


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

    # Controls looping over json pagination 
    page_size = '20'
    page_count = 10
    locale = '*'
    iterative_range = range(1,page_count,1)


    for page in iterative_range:
        query = {'apikey' : ticketmaster_key , 'locale' : locale ,'city': city, 'state': state, 'countryCode': country, 'radius': search_radius, 'segmentName': segment_name, 'size': page_size, 'page' : str(page)}
        # data = requests.get(root_url, params=query).json()
        module_dir = os.path.dirname(__file__)  # get current directory
        file_path = os.path.join(module_dir, './tests/test.json')
        with open(file_path) as test_json:
            data = json.load(test_json)
        
        # TODO If pages > 1 Loop over pages
        page_count = data['page']['totalPages']

        if is_valid_json(data):
            propogate_db(data)
            return HttpResponse(f'Data recieved.')
        else:
            return HttpResponse(f'Error. Response recieved:\n{data}')


# get details on each show
def find_show_details(show_id):
    # TODO Refresh specific show details using show id
    pass

def propogate_db(data):
    # TODO Check if unique id exists for all of these


    for show in data['_embedded']['events']:
        add_venue(['_embedded']['venues']['name'])
        add_artist(['_embedded']['venues']['name'])
        add_show(['id'],['date']['start']['dateTime'],[])
    # TODO Add Venues
    # TODO Add Artists    
    pass

def add_venue(id, venue_name, venue_city, venue_state):
    Venue(name = venue_name,  city = venue_city, state = venue_state).save()
    pass

def add_artist(id, artist_name):
    Artist(name = artist_name).save()
    pass


def add_show(id,show_date, show_artist, show_venue):
    Show(date = show_date, artist =show_artist, venue = show_venue).save()
    
    pass

def is_valid_json(jsonData): 
#Returns a value error if the json is invalid and returns false, otherwise returns true.
    try:
        if (type(jsonData) == dict):
            return True
        elif (type(jsonData) == str):
            json.loads(jsonData)
            return True
    except ValueError as err:
        return False


