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

import mock
from ..admin_views import *

def mock_tickmaster_json():
    mock_response = open('test.json')
    mock_data = json.load(mock_response)
    return mock_data



class FindShowsTest(TestCase):
    def setUp(self):

        return super().setUp()

    root_url = 'https://catfact.ninja/fact'

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

            with open('test.json') as test_json:
                test_data = json.load(test_json)
            response = is_valid_json(test_data)
            self.assertTrue(response)