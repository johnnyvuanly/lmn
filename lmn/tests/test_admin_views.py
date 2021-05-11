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
class MyGreatClassTestCase(TestCase):

    # We patch 'requests.get' with our own method. The mock object is passed in to our test case method.
    @mock.patch('requests.get', side_effect=mocked_requests_get)
    def test_fetch(self, mock_get):

        file_path = os.path.join(module_dir, 'test.json')
        with open(file_path) as test_json:
            test_data = json.load(test_json)

        # Assert requests.get calls
        fshows = find_shows()
        json_data = fshows.fetch_json('test.json')
        self.assertEqual(json_data, {"key1": "value1"})
        json_data = fshows.fetch_json('http://someotherurl.com/anothertest.json')
        self.assertEqual(json_data, {"key2": "value2"})
        json_data = fshows.fetch_json('http://nonexistenturl.com/cantfindme.json')
        self.assertIsNone(json_data)

        # We can even assert that our mocked method was called with the right parameters
        self.assertIn(mock.call('http://someurl.com/test.json'), mock_get.call_args_list)
        self.assertIn(mock.call('http://someotherurl.com/anothertest.json'), mock_get.call_args_list)

        self.assertEqual(len(mock_get.call_args_list), 3)
class FindShowsTest(TestCase):

    
    def test_find_shows(self):

        #self.assertRaises
        pass

    def test_add_show(self):
        pass

    def test_add_artist(self):
        pass

    def test_add_venue(self):
        test_venue = ['U.S. Bank Stadium', 'Minneapolis', 'MN', 'KovZpZAF6ttA']
        pass




class ValidJsonTest(TestCase):

        def test_is_valid_json(self):
            #Check invalid json - https://pynative.com/python-json-validation/
            test_json = """{"name": "jane doe", "salary": 9000, "email": "jane.doe@pynative.com",}"""
            response = is_valid_json(test_json)
            self.assertFalse(response)

            #Check valid json - https://pynative.com/python-json-validation/
            test_json = """{"name": "jane doe", "salary": 9000, "email": "jane.doe@pynative.com"}"""
            response = is_valid_json(test_json)
            self.assertTrue(response)

            module_dir = os.path.dirname(__file__)  # get current directory
            file_path = os.path.join(module_dir, 'test.json')
            with open(file_path) as test_json:
                test_data = json.load(test_json)
            response = is_valid_json(test_data)
            self.assertTrue(response)