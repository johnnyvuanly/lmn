from django.db import models

from django.db import models
from django.contrib.auth.models import User
import datetime
from django.core.files.storage import default_storage

""" All the models for the application """

# Every model gets a primary key field by default.

# Users, venues, shows, artists, notes

# User is provided by Django. The email field is not unique by
# default, so add this to prevent more than one user with the same email.
User._meta.get_field('email')._unique = True

#Require email, first name and last name
User._meta.get_field('email')._blank = False
User._meta.get_field('last_name')._blank = False
User._meta.get_field('first_name')._blank = False

rating_list = (('', ''), ('Horrible', "Horrible"), ('Average', 'Average'), ('Good', 'Good'), ('Amazing', 'Amazing'))


class Profile(models.Model):
    """ Information for users adding a bio to their profile """
    bio = models.TextField(max_length=500, blank=True)
    user = models.OneToOneField(User, on_delete=models.CASCADE)

class Artist(models.Model):
    """ A music artist """
    name = models.CharField(max_length=200, blank=False)

    def __str__(self):
        """ return a string """
        return f'Name: {self.name}'

class Venue(models.Model):
    """ A venue, that hosts shows. """
    name = models.CharField(max_length=200, blank=False, unique=True)
    city = models.CharField(max_length=200, blank=False)
    state = models.CharField(max_length=2, blank=False) 

    def __str__(self):
        """ return a string """
        return f'Name: {self.name} Location: {self.city}, {self.state}'

class Show(models.Model):
    """ A show - one artist playing at one venue at a particular date. """
    show_date = models.DateTimeField(blank=False)
    artist = models.ForeignKey(Artist, on_delete=models.CASCADE)
    venue = models.ForeignKey(Venue, on_delete=models.CASCADE)

    def __str__(self):
        """ return a string """
        return f'Artist: {self.artist} At: {self.venue} On: {self.show_date}'


class Note(models.Model):
    """ One user's opinion of one show. """
    show = models.ForeignKey(Show, blank=False, on_delete=models.CASCADE)
    user = models.ForeignKey('auth.User', blank=False, on_delete=models.CASCADE)
    title = models.CharField(max_length=200, blank=False)
    text = models.TextField(max_length=1000, blank=False)
    posted_date = models.DateTimeField(auto_now_add=True, blank=False)
    photo = models.ImageField(upload_to='lmn/media/user_images/', blank=True, null=True)
    rating = models.CharField(max_length=8, choices=rating_list, default='0')

    def save(self, *args, **kwargs):
        """ Save the note """
        old_note = Note.objects.filter(pk=self.pk).first()
        if old_note and old_note.photo:
            if old_note.photo != self.photo:
                self.delete_photo(old_note.photo)

        super().save(*args, **kwargs)

        

    def delete(self, *args, **kwargs):
        """ Delete the note """
        if self.photo:
            self.delete_photo(self.photo)
        
        super().delete(*args, **kwargs)

    def delete_photo(self, photo):
        """ delete the photo """
        if default_storage.exists(photo.name):
            default_storage.delete(photo.name)

    def __str__(self):
        """ return a string for a full note """
        photo_str = self.photo.url if self.photo else 'no photo'
        return f'User: {self.user} Show: {self.show} Note title: {self.title} Text: {self.text} Posted on: {self.posted_date}, Photo: {photo_str}'


