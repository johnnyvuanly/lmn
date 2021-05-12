from django.test import TestCase, Client

from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import authenticate

from lmn.models import Venue, Artist, Note, Show
from django.contrib.auth.models import User

import requests
import os
import json
from django.http import HttpResponse

from unittest import TestCase, mock
from unittest.mock import patch
from ..admin_views import *

def mock_tickmaster_json():
    module_dir = os.path.dirname(__file__)  # get current directory
    file_path = os.path.join(module_dir, 'test.json')
    with open(file_path) as test_json:
        mock_data = json.load(test_json)
    return mock_data

# This method will be used by the mock to replace requests.get
def mocked_requests_get(*args, **kwargs):
    class MockResponse:
        def __init__(self, json_data, status_code):
            self.json_data = json_data
            self.status_code = status_code

        def json(self):
            return self.json_data

    if args[0] == 'http://someurl.com/test.json':
        return MockResponse({"key1": "value1"}, 200)
    elif args[0] == 'http://someotherurl.com/anothertest.json':
        return MockResponse({"key2": "value2"}, 200)

    return MockResponse(None, 404)

# Our test case class
# class MyGreatClassTestCase(TestCase):

#     # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
#     @mock.patch('requests.get', side_effect=mocked_requests_get)
#     def test_fetch(self, mock_get):

#         file_path = os.path.join(module_dir, 'test.json')
#         with open(file_path) as test_json:
#             test_data = json.load(test_json)

#         # Assert requests.get calls
#         fshows = find_shows()
#         json_data = fshows.fetch_json('test.json')
#         self.assertEqual(json_data, {"key1": "value1"})
#         json_data = fshows.fetch_json('http://someotherurl.com/anothertest.json')
#         self.assertEqual(json_data, {"key2": "value2"})
#         json_data = fshows.fetch_json('http://nonexistenturl.com/cantfindme.json')
#         self.assertIsNone(json_data)

#         # We can even assert that our mocked method was called with the right parameters
#         self.assertIn(mock.call('http://someurl.com/test.json'), mock_get.call_args_list)
#         self.assertIn(mock.call('http://someotherurl.com/anothertest.json'), mock_get.call_args_list)

#         self.assertEqual(len(mock_get.call_args_list), 3)
class FindShowsTest(TestCase):

    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_find_shows(self, mock_get):
        module_dir = os.path.dirname(__file__)  # get current directory
        file_path = os.path.join(module_dir, 'test.json')
        with open(file_path) as test_json:
            mock_data = json.load(test_json)

        # Test HTTPSResponse
        mock_get.return_value.status_code = 200
        response = find_shows()
        expected_response = 200        
        self.assertEqual(expected_response,response.status_code)

        # Test  


        # self.assertEqual(json_data, {"key1": "value1"})
        # json_data = fshows.data('https://jsonplaceholder.typicode.com/posts/1') # https://jsonplaceholder.typicode.com/ Test API provided by typicode.
        # self.assertEqual(json_data, {"key2": "value2"})
        # json_data = fshows.data('http://nonexistenturl.com/cantfindme.json')
        # self.assertIsNone(json_data)
        pass

    def test_add_show(self):
        test_artist = ['JSIFSnfiasd', 'Beck']
        test_venue = ['U.S. Bank Stadium', 'Minneapolis', 'MN', 'KovZpZAF6ttA']
        artist = add_artist(test_artist[0], test_artist[1])
        venue = add_venue( test_venue[3], test_venue[0], test_venue[1], test_venue[2], )
        show_date = datetime.datetime.now()
        response = add_show('blablabla',show_date,artist,venue)
        self.assertEqual('blablabla',response.api_id)
        self.assertEqual(show_date,response.date,f"This test was expecting {show_date} and recieved {response}")
        self.assertEqual(test_artist[1],response.artist.name,f"This test was expecting {test_artist[1]} and recieved {response}")
        self.assertEqual(test_venue[3],response.venue.api_id,f"This test was expecting {test_venue[3]} and recieved {response}")


        pass

    def test_add_artist(self):
        test_artist = ['JSIFSnfiasd', 'Beck']
        expected_response = 'Beck'
        response = add_artist(test_artist[0], test_artist[1])
        self.assertEqual(expected_response,response.name,f"This test was expecting {expected_response} and recieved {response}")
        pass

    def test_add_venue(self):
        # Test creation of new venue
        test_venue = ['U.S. Bank Stadium', 'Minneapolis', 'MN', 'KovZpZAF6ttA']
        expected_response = 'U.S. Bank Stadium'
        response = add_venue( test_venue[3], test_venue[0], test_venue[1], test_venue[2], )
        self.assertEqual(expected_response,response.name,f"This test was expecting {expected_response} and recieved {response}")

        # Test creation of new venue
        add_venue('KovZpZAF6ttA', 'U.S. Bank Stadium', 'Minneapolis', 'MN')
        test_venue = ['Armory', 'Minneapolis', 'MN', 'KovZpZAF6ttA']
        expected_response = 'U.S. Bank Stadium'
        response = add_venue( test_venue[3], test_venue[0], test_venue[1], test_venue[2], )
        self.assertNotEqual(expected_response,response.name,f"This test was expecting {expected_response} and recieved {response}")

        # Test handling of incorrect input
        test_venue = ['Armory', 'Minneapolis', 'Minnesota', 'KovZpZAF6ttA']
        response = add_venue( test_venue[3], test_venue[0], test_venue[1], test_venue[2], )
        self.assertRaises(expected_response,response.name,f"This test was expecting {expected_response} and recieved {response}")

