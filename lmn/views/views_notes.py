from django.shortcuts import render, redirect, get_object_or_404

from ..models import Venue, Artist, Note, Show
from ..forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.http import HttpResponseForbidden
from django.contrib import messages

@login_required
def new_note(request, show_pk):

    show = get_object_or_404(Show, pk=show_pk)

    if request.method == 'POST':
        form = NewNoteForm(request.POST, request.FILES)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.show = show
            note.save()
            messages.info(request, 'Note Successfully Added/Updated')
            return redirect('note_detail', note_pk=note.pk)

    else :
        form = NewNoteForm()
    return render(request, 'lmn/notes/new_note.html' , { 'form': form , 'show': show })

@login_required
def latest_notes(request):

    notes = Note.objects.all().order_by('-posted_date')
    return render(request, 'lmn/notes/note_list.html', { 'notes': notes })

@login_required
def notes_for_show(request, show_pk):

    show = Show.objects.get(pk=show_pk)
    notes = Note.objects.filter(show=show_pk).order_by('-posted_date') # Display notes for specific show, sorted by posted date
    return render(request, 'lmn/notes/note_list.html', { 'show': show, 'notes': notes })

@login_required
def note_detail(request, note_pk):

    note = get_object_or_404(Note, pk=note_pk)
    return render(request, 'lmn/notes/note_detail.html' , { 'note': note })
