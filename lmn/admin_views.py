import requests
from .models import *
from .forms import *
import json
from django.http import HttpResponse



def cat_facts(request):
    return HttpResponse(f'Cats are animals')


def find_shows(request):
    # Search Parameters
    root_url = 'https://app.ticketmaster.com/discovery/v2/'
    # show_url = f'/{show_id}' # add this to get details on a specific show
    city = 'Minneapolis'
    state = 'mn'
    country = 'US'
    search_radius = '50'
    segment_name = 'music'
    page_size = '99'

    query = {'apikey' : os.environ.get('TicketMasterKey'), 'city': city, 'state': state, 'country': country, 'radius':search_radius, 'segment': segment_name, 'size': page_size}
    response = requests.get(root_url, params=query)
    response.raise_for_status()
    data = response.json()
    # TODO If pages > 1 Loop over pages
    if is_valid_json(data):
        propogate_db(data)
        return HttpResponse(f'Data recieved:\n{data}')


# get details on each show
def find_show_details(self):
    # TODO Refresh specific show details using show id
    pass

def propogate_db(self, data):
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


