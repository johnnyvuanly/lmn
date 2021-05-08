import tempfile
import os

from django.http import response
from django.test import TestCase, Client

from django.urls import reverse
from django.contrib import auth
from django.contrib.auth import authenticate

from lmn.models import Venue, Artist, Note, Show
from django.contrib.auth.models import User

import re, datetime
from datetime import timezone

from PIL import Image



# TODO verify correct templates are rendered.

class TestEmptyViews(TestCase):

    ''' main views - the ones in the navigation menu'''
    def test_with_no_artists_returns_empty_list(self):
        response = self.client.get(reverse('artist_list'))
        self.assertFalse(response.context['artists'])  # An empty list is false

    def test_with_no_venues_returns_empty_list(self):
        response = self.client.get(reverse('venue_list'))
        self.assertFalse(response.context['venues'])  # An empty list is false

    def test_with_no_notes_returns_empty_list(self):
        response = self.client.get(reverse('latest_notes'))
        self.assertFalse(response.context['notes'])  # An empty list is false


class TestArtistViews(TestCase):

    fixtures = ['testing_artists', 'testing_venues', 'testing_shows']

    def test_all_artists_displays_all_alphabetically(self):
        response = self.client.get(reverse('artist_list'))

        # .* matches 0 or more of any character. Test to see if
        # these names are present, in the right order

        regex = '.*ACDC.*REM.*Yes.*'
        response_text = str(response.content)

        self.assertTrue(re.match(regex, response_text))
        self.assertEqual(len(response.context['artists']), 3)


    def test_artists_search_clear_link(self):
        response = self.client.get( reverse('artist_list') , {'search_name' : 'ACDC'} )

        # There is a clear link, it's url is the main venue page
        all_artists_url = reverse('artist_list')
        self.assertContains(response, all_artists_url)


    def test_artist_search_no_search_results(self):
        response = self.client.get( reverse('artist_list') , {'search_name' : 'Queen'} )
        self.assertNotContains(response, 'Yes')
        self.assertNotContains(response, 'REM')
        self.assertNotContains(response, 'ACDC')
        # Check the length of artists list is 0
        self.assertEqual(len(response.context['artists']), 0)


    def test_artist_search_partial_match_search_results(self):

        response = self.client.get(reverse('artist_list'), {'search_name' : 'e'})
        # Should be two responses, Yes and REM
        self.assertContains(response, 'Yes')
        self.assertContains(response, 'REM')
        self.assertNotContains(response, 'ACDC')
        # Check the length of artists list is 2
        self.assertEqual(len(response.context['artists']), 2)


    def test_artist_search_one_search_result(self):

        response = self.client.get(reverse('artist_list'), {'search_name' : 'ACDC'} )
        self.assertNotContains(response, 'REM')
        self.assertNotContains(response, 'Yes')
        self.assertContains(response, 'ACDC')
        # Check the length of artists list is 1
        self.assertEqual(len(response.context['artists']), 1)


    def test_correct_template_used_for_artists(self):
        # Show all
        response = self.client.get(reverse('artist_list'))
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')

        # Search with matches
        response = self.client.get(reverse('artist_list'), {'search_name' : 'ACDC'} )
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')
        # Search no matches
        response = self.client.get(reverse('artist_list'), {'search_name' : 'Non Existant Band'})
        self.assertTemplateUsed(response, 'lmn/artists/artist_list.html')

        # Artist detail
        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk':1}))
        self.assertTemplateUsed(response, 'lmn/artists/artist_detail.html')

        # Artist list for venue
        response = self.client.get(reverse('artists_at_venue', kwargs={'venue_pk':1}))
        self.assertTemplateUsed(response, 'lmn/artists/artist_list_for_venue.html')


    def test_artist_detail(self):

        ''' Artist 1 details displayed in correct template '''
        # kwargs to fill in parts of url. Not get or post params

        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk' : 1} ))
        self.assertContains(response, 'REM')
        self.assertEqual(response.context['artist'].name, 'REM')
        self.assertEqual(response.context['artist'].pk, 1)


    def test_get_artist_that_does_not_exist_returns_404(self):
        response = self.client.get(reverse('artist_detail', kwargs={'artist_pk' : 10} ))
        self.assertEqual(response.status_code, 404)


    def test_venues_played_at_most_recent_shows_first(self):
        ''' For each artist, display a list of venues they have played shows at '''

        # Artist 1 (REM) has played at venue 2 (Turf Club) on two dates

        url = reverse('venues_for_artist', kwargs={'artist_pk':1})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        show1, show2 = shows[0], shows[1]
        self.assertEqual(2, len(shows))

        self.assertEqual(show1.artist.name, 'REM')
        self.assertEqual(show1.venue.name, 'The Turf Club')

        # From the fixture, show 2's "show_date": "2017-02-02T19:30:00-06:00"
        expected_date = datetime.datetime(2017, 2, 2, 19, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(show1.show_date, expected_date)

        # from the fixture, show 1's "show_date": "2017-01-02T17:30:00-00:00",
        self.assertEqual(show2.artist.name, 'REM')
        self.assertEqual(show2.venue.name, 'The Turf Club')
        expected_date = datetime.datetime(2017, 1, 2, 17, 30, 0, tzinfo=timezone.utc)
        self.assertEqual(show2.show_date, expected_date)

        # Artist 2 (ACDC) has played at venue 1 (First Ave)

        url = reverse('venues_for_artist', kwargs={'artist_pk': 2})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        show1 = shows[0]
        self.assertEqual(1, len(shows))

        # This show has "show_date": "2017-01-21T21:45:00-00:00",
        self.assertEqual(show1.artist.name, 'ACDC')
        self.assertEqual(show1.venue.name, 'First Avenue')
        expected_date = datetime.datetime(2017, 1, 21, 21, 45, 0, tzinfo=timezone.utc)
        self.assertEqual(show1.show_date, expected_date)

        # Artist 3 , no shows

        url = reverse('venues_for_artist', kwargs={'artist_pk':3})
        response = self.client.get(url)
        shows = list(response.context['shows'].all())
        self.assertEqual(0, len(shows))



class TestVenues(TestCase):

        fixtures = ['testing_venues', 'testing_artists', 'testing_shows']

        def test_with_venues_displays_all_alphabetically(self):
            response = self.client.get(reverse('venue_list'))

            # .* matches 0 or more of any character. Test to see if
            # these names are present, in the right order

            regex = '.*First Avenue.*Target Center.*The Turf Club.*'
            response_text = str(response.content)

            self.assertTrue(re.match(regex, response_text))

            self.assertEqual(len(response.context['venues']), 3)
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')


        def test_venue_search_clear_link(self):
            response = self.client.get( reverse('venue_list') , {'search_name' : 'Fine Line'} )

            # There is a clear link, it's url is the main venue page
            all_venues_url = reverse('venue_list')
            self.assertContains(response, all_venues_url)


        def test_venue_search_no_search_results(self):
            response = self.client.get( reverse('venue_list') , {'search_name' : 'Fine Line'} )
            self.assertNotContains(response, 'First Avenue')
            self.assertNotContains(response, 'Turf Club')
            self.assertNotContains(response, 'Target Center')
            # Check the length of venues list is 0
            self.assertEqual(len(response.context['venues']), 0)
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')


        def test_venue_search_partial_match_search_results(self):
            response = self.client.get(reverse('venue_list'), {'search_name' : 'c'})
            # Should be two responses, Yes and REM
            self.assertNotContains(response, 'First Avenue')
            self.assertContains(response, 'Turf Club')
            self.assertContains(response, 'Target Center')
            # Check the length of venues list is 2
            self.assertEqual(len(response.context['venues']), 2)
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')


        def test_venue_search_one_search_result(self):

            response = self.client.get(reverse('venue_list'), {'search_name' : 'Target'} )
            self.assertNotContains(response, 'First Avenue')
            self.assertNotContains(response, 'Turf Club')
            self.assertContains(response, 'Target Center')
            # Check the length of venues list is 1
            self.assertEqual(len(response.context['venues']), 1)
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')


        def test_venue_detail(self):

            ''' venue 1 details displayed in correct template '''
            # kwargs to fill in parts of url. Not get or post params

            response = self.client.get(reverse('venue_detail', kwargs={'venue_pk' : 1} ))
            self.assertContains(response, 'First Avenue')
            self.assertEqual(response.context['venue'].name, 'First Avenue')
            self.assertEqual(response.context['venue'].pk, 1)

            self.assertTemplateUsed(response, 'lmn/venues/venue_detail.html')


        def test_get_venue_that_does_not_exist_returns_404(self):
            response = self.client.get(reverse('venue_detail', kwargs={'venue_pk' : 10} ))
            self.assertEqual(response.status_code, 404)


        def test_artists_played_at_venue_most_recent_first(self):
            # Artist 1 (REM) has played at venue 2 (Turf Club) on two dates

            url = reverse('artists_at_venue', kwargs={'venue_pk':2})
            response = self.client.get(url)
            shows = list(response.context['shows'].all())
            show1, show2 = shows[0], shows[1]
            self.assertEqual(2, len(shows))

            self.assertEqual(show1.artist.name, 'REM')
            self.assertEqual(show1.venue.name, 'The Turf Club')

            expected_date = datetime.datetime(2017, 2, 2, 19, 30, 0, tzinfo=timezone.utc)
            self.assertEqual(show1.show_date, expected_date)

            self.assertEqual(show2.artist.name, 'REM')
            self.assertEqual(show2.venue.name, 'The Turf Club')
            expected_date = datetime.datetime(2017, 1, 2, 17, 30, 0, tzinfo=timezone.utc)
            self.assertEqual(show2.show_date, expected_date)

            # Artist 2 (ACDC) has played at venue 1 (First Ave)

            url = reverse('artists_at_venue', kwargs={'venue_pk': 1})
            response = self.client.get(url)
            shows = list(response.context['shows'].all())
            show1 = shows[0]
            self.assertEqual(1, len(shows))

            self.assertEqual(show1.artist.name, 'ACDC')
            self.assertEqual(show1.venue.name, 'First Avenue')
            expected_date = datetime.datetime(2017, 1, 21, 21, 45, 0, tzinfo=timezone.utc)
            self.assertEqual(show1.show_date, expected_date)

            # Venue 3 has not had any shows

            url = reverse('artists_at_venue', kwargs={'venue_pk':3})
            response = self.client.get(url)
            shows = list(response.context['shows'].all())
            self.assertEqual(0, len(shows))


        def test_correct_template_used_for_venues(self):
            # Show all
            response = self.client.get(reverse('venue_list'))
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

            # Search with matches
            response = self.client.get(reverse('venue_list'), {'search_name' : 'First'} )
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')
            # Search no matches
            response = self.client.get(reverse('venue_list'), {'search_name' : 'Non Existant Venue'})
            self.assertTemplateUsed(response, 'lmn/venues/venue_list.html')

            # Venue detail
            response = self.client.get(reverse('venue_detail', kwargs={'venue_pk':1}))
            self.assertTemplateUsed(response, 'lmn/venues/venue_detail.html')

            response = self.client.get(reverse('artists_at_venue', kwargs={'venue_pk':1}))
            self.assertTemplateUsed(response, 'lmn/artists/artist_list_for_venue.html')



class TestAddNoteUnauthentictedUser(TestCase):

    fixtures = [ 'testing_artists', 'testing_venues', 'testing_shows' ]  # Have to add artists and venues because of foreign key constrains in show

    def test_add_note_unauthenticated_user_redirects_to_login(self):
        response = self.client.get( '/notes/add/1/', follow=True)  # Use reverse() if you can, but not required.
        # Should redirect to login; which will then redirect to the notes/add/1 page on success.
        self.assertRedirects(response, '/accounts/login/?next=/notes/add/1/')


class TestAddNotesWhenUserLoggedIn(TestCase):
    fixtures = ['testing_users', 'testing_artists', 'testing_shows', 'testing_venues', 'testing_notes']

    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)


    def test_save_note_for_non_existent_show_is_error(self):
        new_note_url = reverse('new_note', kwargs={'show_pk':100})
        response = self.client.post(new_note_url)
        self.assertEqual(response.status_code, 404)


    def test_can_save_new_note_for_show_blank_data_is_error(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('new_note', kwargs={'show_pk':1})

        # No post params
        response = self.client.post(new_note_url, follow=True)
        # No note saved, should show same page
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # no title
        response = self.client.post(new_note_url, {'text':'blah blah' }, follow=True)
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # no text
        response = self.client.post(new_note_url, {'title':'blah blah' }, follow=True)
        self.assertTemplateUsed('lmn/notes/new_note.html')

        # nothing added to database
        self.assertEqual(Note.objects.count(), initial_note_count)   # 2 test notes provided in fixture, should still be 2


    def test_add_note_database_updated_correctly(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('new_note', kwargs={'show_pk':1})

        response = self.client.post(new_note_url, {'text':'ok', 'title':'blah blah' }, follow=True)

        # Verify note is in database
        new_note_query = Note.objects.filter(text='ok', title='blah blah')
        self.assertEqual(new_note_query.count(), 1)

        # And one more note in DB than before
        self.assertEqual(Note.objects.count(), initial_note_count + 1)

        # Date correct?
        now = datetime.datetime.today()
        posted_date = new_note_query.first().posted_date
        self.assertEqual(now.date(), posted_date.date())  # TODO check time too


    def test_redirect_to_note_detail_after_save(self):

        initial_note_count = Note.objects.count()

        new_note_url = reverse('new_note', kwargs={'show_pk':1})
        response = self.client.post(new_note_url, {'text':'ok', 'title':'blah blah' }, follow=True)
        new_note = Note.objects.filter(text='ok', title='blah blah').first()

        self.assertRedirects(response, reverse('note_detail', kwargs={'note_pk': new_note.pk }))


class TestUserProfile(TestCase):
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show

    # verify correct list of reviews for a user
    def test_user_profile_show_list_of_their_notes(self):
        # get user profile for user 2. Should have 2 reviews for show 1 and 2.
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':2}))
        notes_expected = list(Note.objects.filter(user=2).order_by('-posted_date'))
        notes_provided = list(response.context['notes'])
        self.assertTemplateUsed('lmn/users/user_profile.html')
        self.assertEqual(notes_expected, notes_provided)

        # test notes are in date order, most recent first.
        # Note PK 3 should be first, then PK 2
        first_note = response.context['notes'][0]
        self.assertEqual(first_note.pk, 3)

        second_note = response.context['notes'][1]
        self.assertEqual(second_note.pk, 2)


    def test_user_with_no_notes(self):
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':3}))
        self.assertFalse(response.context['notes'])


    def test_username_shown_on_profile_page(self):
        # A string "username's notes" is visible
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':1}))
        self.assertContains(response, 'alice\'s notes')
        
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':2}))
        self.assertContains(response, 'bob\'s notes')


    def test_correct_user_name_shown_different_profiles(self):
        logged_in_user = User.objects.get(pk=2)
        self.client.force_login(logged_in_user)  # bob
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':2}))
        self.assertContains(response, 'You are logged in, <a href="/user/profile/2/">bob</a>.')
        
        # Same message on another user's profile. Should still see logged in message 
        # for currently logged in user, in this case, bob
        response = self.client.get(reverse('user_profile', kwargs={'user_pk':3}))
        self.assertContains(response, 'You are logged in, <a href="/user/profile/2/">bob</a>.')
        

class TestNotes(TestCase):
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show

    def test_latest_notes(self):
        response = self.client.get(reverse('latest_notes'))
        expected_notes = list(Note.objects.all())
        # Should be note 3, then 2, then 1
        context = response.context['notes']
        first, second, third = context[0], context[1], context[2]
        self.assertEqual(first.pk, 3)
        self.assertEqual(second.pk, 2)
        self.assertEqual(third.pk, 1)


    def test_notes_for_show_view(self):
        # Verify correct list of notes shown for a Show, most recent first
        # Show 1 has 2 notes with PK = 2 (most recent) and PK = 1
        response = self.client.get(reverse('notes_for_show', kwargs={'show_pk':1}))
        context = response.context['notes']
        first, second = context[0], context[1]
        self.assertEqual(first.pk, 2)
        self.assertEqual(second.pk, 1)


    def test_correct_templates_uses_for_notes(self):
        response = self.client.get(reverse('latest_notes'))
        self.assertTemplateUsed(response, 'lmn/notes/note_list.html')

        response = self.client.get(reverse('note_detail', kwargs={'note_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/note_detail.html')

        response = self.client.get(reverse('notes_for_show', kwargs={'show_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/note_list.html')

        # Log someone in
        self.client.force_login(User.objects.first())
        response = self.client.get(reverse('new_note', kwargs={'show_pk':1}))
        self.assertTemplateUsed(response, 'lmn/notes/new_note.html')



class TestUserAuthentication(TestCase):

    ''' Some aspects of registration (e.g. missing data, duplicate username) covered in test_forms '''
    ''' Currently using much of Django's built-in login and registration system'''

    def test_user_registration_logs_user_in(self):
        response = self.client.post(reverse('register'), {'username':'sam12345', 'email':'sam@sam.com', 'password1':'feRpj4w4pso3az', 'password2':'feRpj4w4pso3az', 'first_name':'sam', 'last_name' : 'sam'}, follow=True)

        # Assert user is logged in - one way to do it...
        user = auth.get_user(self.client)
        self.assertEqual(user.username, 'sam12345')

        # This works too. Don't need both tests, added this one for reference.
        # sam12345 = User.objects.filter(username='sam12345').first()
        # auth_user_id = int(self.client.session['_auth_user_id'])
        # self.assertEqual(auth_user_id, sam12345.pk)


    def test_user_registration_redirects_to_correct_page(self):
        # TODO If user is browsing site, then registers, once they have registered, they should
        # be redirected to the last page they were at, not the homepage.
        response = self.client.post(reverse('register'), {'username':'sam12345', 'email':'sam@sam.com', 'password1':'feRpj4w4pso3az@1!2', 'password2':'feRpj4w4pso3az@1!2', 'first_name':'sam', 'last_name' : 'sam'}, follow=True)
        new_user = authenticate(username='sam12345', password='feRpj4w4pso3az@1!2')
        self.assertRedirects(response, reverse('user_profile', kwargs={"user_pk": new_user.pk}))   
        self.assertContains(response, 'sam12345')  # page has user's name on it

class TestDeleteNotes(TestCase):
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show
    def setUp(self):
        user = User.objects.first()
        self.client.force_login(user)
    
    def test_delete_note(self):
        response = self.client.post(reverse('delete_note', args=(1,)), follow=True)
        place_2 = Note.objects.filter(pk=1).first()
        self.assertIsNone(place_2)

    def test_deleting_somebodys_note_that_is_not_yours_doesnt_work(self):
        response = self.client.post(reverse('delete_note', args=(2,)), follow=True)
        self.assertEqual(403, response.status_code)
        place_5 = Note.objects.get(pk=2)
        self.assertIsNotNone(place_5)
    

class TestImageUpload(TestCase):
    fixtures = [ 'testing_users', 'testing_artists', 'testing_venues', 'testing_shows', 'testing_notes' ]  # Have to add artists and venues because of foreign key constrains in show

    def setUp(self):
        user = User.objects.get(pk=1)
        self.client.force_login(user)
        self.MEDIA_ROOT = tempfile.mkdtemp()

    def tearDown(self):
        print('todo delete temp directory, temp image')
    
    def create_temp_image_file(self):
        handle, tmp_image_file = tempfile.mkstemp(suffix='.jpg')
        img = Image.new('RGB', (10, 10) )
        img.save(tmp_image_file, format='JPEG')
        return tmp_image_file

    def test_upload_new_image_for_own_note(self):
        
        img_file_path = self.create_temp_image_file()

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(img_file_path, 'rb') as first_img_file:

                resp = self.client.post(reverse('edit_note', kwargs={'note_pk': 1} ), {'photo': first_img_file }, follow=True)

                place_1 = Note.objects.get(pk=1)

                first_uploaded_image = place_1.photo.name


                first_path = os.path.join(self.MEDIA_ROOT, first_uploaded_image)

                self.assertTrue(os.path.exists(first_path))
    
    def test_edit_note_for_own_note_expect_old_changed(self):

        response = self.client.post(reverse('edit_note', kwargs={'note_pk': 1}), {'title': 'lame','text':'awesome'}, follow=True)
        updated_note_1 = Note.objects.get(pk=1)
        self.assertEqual(response.context['note'], updated_note_1)
        self.assertContains(response, 'awesome')  # new text shown
    
    def test_modify_someone_else_notes_not_authorized(self):
        response = self.client.post(reverse('edit_note', kwargs={'note_pk':3}), {'notes':'awesome'}, follow=True)
        self.assertEqual(403, response.status_code)   # 403 Forbidden 
       
    def test_edit_image_for_own_note_expect_old_deleted(self):
        
        first_img_file_path = self.create_temp_image_file()
        second_img_file_path = self.create_temp_image_file()

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(first_img_file_path, 'rb') as first_img_file:

                resp = self.client.post(reverse('edit_note', kwargs={'note_pk': 1} ), {'photo': first_img_file }, follow=True)

                place_1 = Note.objects.get(pk=1)

                first_uploaded_image = place_1.photo.name

                with open(second_img_file_path, 'rb') as second_img_file:
                    resp = self.client.post(reverse('edit_note', kwargs={'note_pk': 1}), {'photo': second_img_file}, follow=True)

                    # first file should not exist 
                    # second file should exist 

                    place_1 = Note.objects.get(pk=1)

                    second_uploaded_image = place_1.photo.name

                    first_path = os.path.join(self.MEDIA_ROOT, first_uploaded_image)
                    second_path = os.path.join(self.MEDIA_ROOT, second_uploaded_image)

                    self.assertTrue(os.path.exists(second_path))


    def test_edit_image_for_someone_else_note_doesnt_work(self):

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
  
            img_file = self.create_temp_image_file()
            with open(img_file, 'rb') as image:
                resp = self.client.post(reverse('edit_note', kwargs={'note_pk': 2} ), {'photo': image }, follow=True)
                self.assertEqual(403, resp.status_code)

                place_5 = Note.objects.get(pk=2)
                self.assertFalse(place_5.photo)   # no photo set


    def test_delete_note_with_image_image_deleted(self): 
        
        img_file_path = self.create_temp_image_file()

        with self.settings(MEDIA_ROOT=self.MEDIA_ROOT):
        
            with open(img_file_path, 'rb') as img_file:
                resp = self.client.post(reverse('edit_note', kwargs={'note_pk': 1} ), {'photo': img_file }, follow=True)
                
                self.assertEqual(200, resp.status_code)

                place_1 = Note.objects.get(pk=1)
                img_file_name = os.path.basename(img_file_path)
                
                uploaded_file_path = os.path.join(self.MEDIA_ROOT, 'user_images', img_file_name)

                # delete place 1 
                place_1 = Note.objects.get(pk=1)
                place_1.delete()
                self.assertFalse(os.path.exists(uploaded_file_path))


class TestGoodbyePage(TestCase):

    fixtures = [ 'testing_users' ]

    def test_logout_redirects_to_goodbye_page(self):
        # Log in
        self.client.force_login(User.objects.first())
        # Make a request to the logout page, testing the link of a logout button
        response = self.client.get(reverse('logout'))
        # Check redirect
        self.assertRedirects(response, reverse('goodbye'))

    def test_goodbye_message_displays_when_user_logs_out(self):
        # First make a request to the goodbye page
        url = reverse('goodbye') 
        response = self.client.get(url)
        self.assertContains(response, 'Successfully signed out!!')

    def test_redirects_to_goodbye_page_if_user_is_not_logged_in(self):
        # Make a request to the logout page, testing the link of a logout button
        response = self.client.get(reverse('logout'))
        # Check redirect
        self.assertRedirects(response, reverse('goodbye'))

    
