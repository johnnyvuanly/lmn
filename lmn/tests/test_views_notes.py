
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
        """During testing user with primary key #1 can login and delete notes. Notes get count in database on specific users """  

        response = self.client.post(reverse('delete_notes', args=(1,)), follow=True) # note 1 belongs to user 1 therefore, 
        #user 1 can delete note.

        note_count = Note.objects.count()
        self.assertEqual(2, note_count)# checking database for 2 notes are remaining
        note_1 = Note.objects.filter(pk=1).first()
        self.assertIsNone(note_1)   # note is deleted

    def test_delete_someone_else_notes_not_auth(self):
        response = self.client.post(reverse('delete_notes',  args=(5,)), follow=True)
        self.assertEqual(403, response.status_code)# Display status code 403 if primary key is not 5
        note_5 = Note.objects.get(pk=5)
        self.assertIsNotNone(note_5)    # note still in database
