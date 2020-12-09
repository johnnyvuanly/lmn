from django.contrib import admin

# Register your models here.

from .models import Venue, Artist, Note, Show, UserDetails

admin.site.register(Venue)
admin.site.register(Artist)
admin.site.register(Note)
admin.site.register(Show)
admin.site.register(UserDetails)
