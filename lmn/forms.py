from django import forms
from .models import Note
import os
import requests
import json
import logging

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError


class VenueSearchForm(forms.Form):
    search_name = forms.CharField(label='Venue Name', max_length=200)


class ArtistSearchForm(forms.Form):
    search_name = forms.CharField(label='Artist Name', max_length=200)


class NewNoteForm(forms.ModelForm):
    class Meta:
        model = Note
        fields = ('title', 'text')


class UserRegistrationForm(UserCreationForm):

    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


    def clean_username(self):

        username = self.cleaned_data['username']

        if not username:
            raise ValidationError('Please enter a username')

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('A user with that username already exists')

        return username


    def clean_first_name(self):
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise ValidationError('Please enter your first name')

        return first_name


    def clean_last_name(self):
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise ValidationError('Please enter your last name')

        return last_name


    def clean_email(self):
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError('Please enter an email address')

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with that email address already exists')

        return email


    def save(self, commit=True):
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user


# TicketMaster API Call
class TicketMasterForm(forms.Form):

    # Search Parameters
    root_url = 'https://app.ticketmaster.com/discovery/v2/'
    # event_url = f'/{event_id}' # add this to get details on a specific event
    city = 'Minneapolis'
    state = 'mn'
    country = 'US'
    search_radius = '50'
    segment_name = 'music'
    page_size = '99'
    

    def find_events(self):
        try:
            query = {'distanceUnit':'mi', 'timeType':'departure', 'wp.1': self.start_location, 'wp.2':self.end_location, 'dateTime': self.start_time, 'key': key}
            headers = {'apikey' : os.environ.get('TicketMasterKey')}
            response = requests.get(self.root_url, params=query, headers=headers)
            response.raise_for_status()
            data = response.json()
            if self.is_valid_json(data):
                logging.info(f'Data recieved:\n{data}')
                self.propogate_db(data)
        except Exception as e:
           logging.exception(e)
           logging.exception(response.text)
           return None, e
    
    # get details on each event
    def find_event_details(self):
        pass

    def propogate_db(self, data):
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