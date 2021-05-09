import requests
import os
import json
from django.http import HttpResponse


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
    page_size = '20'
    locale = '*'

    query = {'apikey' : ticketmaster_key , 'locale' : locale ,'city': city, 'state': state, 'countryCode': country, 'radius': search_radius, 'segmentName': segment_name, 'size': page_size}
    data = requests.get(root_url, params=query).json()
    # TODO If pages > 1 Loop over pages
    if is_valid_json(data):
        propogate_db(data)
        return HttpResponse(f'Data recieved:\n{data}')
    else:
        return HttpResponse(f'Error. Response recieved:\n{data}')


# get details on each show
def find_show_details(show_id):
    # TODO Refresh specific show details using show id
    pass

def propogate_db(data):
    # TODO Check if unique id exists for all of these
    # TODO Add shows
    # TODO Add Venues
    # TODO Add Artists    
    pass

def add_show():

    pass

def add_venue():
    pass

def add_artist():
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


