
from django.test import TestCase
from django.urls import reverse
from django.test import override_settings

from django.contrib.auth.models import User

from lmn.models import Venue, Artist, Note, Show

class TestDeleteNotes(TestCase):

    fixtures = ['testing_notes', 'testing_users','testing_artists','testing_shows','testing_venues' ]

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)

    def test_delete_notes(self):
        """During testing user with primary key ID#1 can login and delete notes. Notes get count in database on specific users """  

        response = self.client.post(reverse('delete_notes', args=(1,)), follow=True) # note 1 belongs to user 1 therefore, 
        #user #1 can delete note.

        note_count = Note.objects.count() # Count notes left in database
        self.assertEqual(2, note_count)# checking and counting database for remaining 2 notes
        note_1 = Note.objects.filter(pk=1).first() # Select note 1 with primary key #1 first
        self.assertIsNone(note_1)   # note is deleted

    def test_delete_someone_else_notes_not_auth(self):

        """"Testing database to check unauthorized user with primary key #5 and status code. If they matched,
         database prevents the user from cancelling note and display message. """

        response = self.client.post(reverse('delete_notes',  args=(5,)), follow=True)
        self.assertEqual(404, response.status_code)# Compare status code 404 with primary key #5
        note_5 = Note.objects.get(pk=5) #fetch for ID# 5
        message = "Forbidden. You don't have permissions to access this resource. Please exit." # error message in case if test case got failed
        self.assertIsNotNone(note_5, message) # assertIsNotNone() to check that if input value is not none
