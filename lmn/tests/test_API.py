import tempfile
import filecmp
import os 
import unittest
from django.test import TestCase
from django.urls import reverse
from django.test import override_settings
from django.db.transaction import atomic
from unittest.mock import patch 
from django.contrib.auth.models import User
from ..models import Venue, Artist, Show
from PIL import Image 


class TestTicketMasterAPI(TestCase):

    @patch('requests.Response.json')
    def test_add_new_data_set(self, mock_api_json_response):

        mock_api_json_response.side_effect = [{'_embedded':{'events':[{'_embedded':{'venues':[{'name':'First Ave','state':{'stateCode':'MN'},'city':{'name':'Minneapolis'}}],'attractions':[{'name':'Killed BY Kiwis'}]},'dates':{'start':{'localDate':'2020-10-25','localTime':'20:00:00'}}},{'_embedded':{'venues':[{'name':'Second Ave','state':{'stateCode':'MN'},'city':{'name':'Minneapolis'}}],'attractions':[{'name':'!Okay'}]},'dates':{'start':{'localDate':'2021-12-24','localTime':'10:00:00'}}}]}}]
        response = self.client.get(reverse('admin_get_data'))

        self.assertEqual(200, response.status_code)
    
    @patch('requests.Response.json')
    def test_add_two_data_sets(self, mock_api_json_response):

        mock_api_json_response.side_effect = [{"_embedded":{"events":[{"_embedded":{"venues":[{"name":"First Ave","state":{"stateCode":"MN"},"city":{"name":"Minneapolis"}}],"attractions":[{"name":"Killed BY Kiwis"}]},"dates":{"start":{"localDate":"2020-10-25","localTime":"20:00:00"}}},{"_embedded":{"venues":[{"name":"Babbettes","state":{"stateCode":"MN"},"city":{"name":"Minneapolis"}}],"attractions":[{"name":"!Okay"}]},"dates":{"start":{"localDate":"2020-12-24","localTime":"16:00:00"}}}]}}]
        response = self.client.get(reverse('admin_get_data'))
        self.assertEqual(2, Venue.objects.count())

    @patch('requests.Response.json')
    def test_no_add_duplicates(self, mock_api_json_response):
        # has 2 sets of duplicate data
        mock_api_json_response.side_effect = [{"_embedded":{"events":[{"_embedded":{"venues":[{"name":"First Ave","state":{"stateCode":"MN"},"city":{"name":"Minneapolis"}}],"attractions":[{"name":"Killed BY Kiwis"}]},"dates":{"start":{"localDate":"2020-10-25","localTime":"20:00:00"}}},{"_embedded":{"venues":[{"name":"First Ave","state":{"stateCode":"MN"},"city":{"name":"Minneapolis"}}],"attractions":[{"name":"Killed BY Kiwis"}]},"dates":{"start":{"localDate":"2020-10-25","localTime":"20:00:00"}}}]}}]

        response = self.client.get(reverse('admin_get_data'))
        #should only have added 1 venue
        self.assertEqual(1, Venue.objects.count())



if __name__ == '__main__':
    unittest.main()