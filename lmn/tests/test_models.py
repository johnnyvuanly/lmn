from django.test import TestCase

from django.contrib.auth.models import User
from django.db import IntegrityError

import tempfile
import filecmp
import os 

from django.urls import reverse
from django.test import override_settings

from .models import Note

from PIL import Image

# Create your tests here.

class TestUser(TestCase):

    def test_create_user_duplicate_username_fails(self):

        user = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        user.save()

        user2 = User(username='bob', email='another_bob@bob.com', first_name='bob', last_name='bob')
        with self.assertRaises(IntegrityError):
            user2.save()

    def test_create_user_duplicate_email_fails(self):
        user = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        user.save()

        user2 = User(username='bob', email='bob@bob.com', first_name='bob', last_name='bob')
        with self.assertRaises(IntegrityError):
            user2.save()

class TestImageUpload(TestCase):

    fixtures = ['testing_users', 'testing_artists', 'testing_shows', 'testing_venues', 'testing_notes']

    def setUp(self):
        user = User.objects.get(note_pk=1)
        self.client.force_login(user)
        self.MEDIA_ROOT = tempfile.mkdtemp()

    def tearDown(self):
        print('Deletes temporary directory and temporary image.')

    def create_temp_image(self):
        handle, tmp_img = tempfile.mkstemp(suffix='.jpg')
        img = Image.new('RGB', (10, 10) )
        img.save(tmp_img, format='JPEG')
        return tmp_img
