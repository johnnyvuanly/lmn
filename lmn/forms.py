from django import forms
from .models import Note, Profile

from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.models import User
from django.forms import ValidationError

""" All the classes and forms for the application """


class VenueSearchForm(forms.Form):
    """ Form for searching the venue """
    search_name = forms.CharField(label='Venue Name', max_length=200)


class ArtistSearchForm(forms.Form):
    """ Form for searching through artists """
    search_name = forms.CharField(label='Artist Name', max_length=200)


class NewNoteForm(forms.ModelForm):
    """ Form allowing users to create new notes """
    class Meta:
        model = Note
        fields = ('title', 'text', 'photo')


class ProfileForm(forms.ModelForm):
    """ A Profile form allowing users to add a bio """
    class Meta:
        model = Profile
        fields = ('bio',)

class UserRegistrationForm(UserCreationForm):
    """ A Form to try to allow the user to register """
    class Meta:
        model = User
        fields = ('username', 'first_name', 'last_name', 'email', 'password1', 'password2')


    def clean_username(self):
        """ Make sure the user has an apporpirate username and not the same as others """
        username = self.cleaned_data['username']

        if not username:
            raise ValidationError('Please enter a username')

        if User.objects.filter(username__iexact=username).exists():
            raise ValidationError('A user with that username already exists')

        return username


    def clean_first_name(self):
        """ Make sure users have a clean first name """
        first_name = self.cleaned_data['first_name']
        if not first_name:
            raise ValidationError('Please enter your first name')

        return first_name


    def clean_last_name(self):
        """ Make sure users have a clean last name """
        last_name = self.cleaned_data['last_name']
        if not last_name:
            raise ValidationError('Please enter your last name')

        return last_name


    def clean_email(self):
        """ Make sure users have a clean email """
        email = self.cleaned_data['email']
        if not email:
            raise ValidationError('Please enter an email address')

        if User.objects.filter(email__iexact=email).exists():
            raise ValidationError('A user with that email address already exists')

        return email


    def save(self, commit=True):
        """ Function to have the users save their information """
        user = super(UserRegistrationForm, self).save(commit=False)
        user.username = self.cleaned_data['username']
        user.email = self.cleaned_data['email']
        user.first_name = self.cleaned_data['first_name']
        user.last_name = self.cleaned_data['last_name']

        if commit:
            user.save()

        return user
