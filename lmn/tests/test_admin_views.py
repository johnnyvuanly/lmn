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

class FindShowsTest(TestCase):

    def test_find_shows(self):

        #self.assertRaises
        pass

    def test_add_show(self):
        pass

    def test_add_artist(self):
        pass

    def test_add_venue(self):
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