from django.shortcuts import render, redirect, get_object_or_404

from ..models import Venue, Artist, Note, Show
from ..forms import VenueSearchForm, NewNoteForm, ArtistSearchForm, UserRegistrationForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages



@login_required
def new_note(request, show_pk):

    show = get_object_or_404(Show, pk=show_pk)
    # Checking to see if there are duplicates being entered, mix of stackoverflow/reddit and some luck
    if request.method == 'POST':
        count = 0
        user_pk = request.user.pk
        print(user_pk)
        note_in_db = note_already_exist(show_pk, user_pk)
        if not note_in_db:
            form = NewNoteForm(request.POST, request.FILES)
            if form.is_valid():
                count += 1
                note = form.save(commit=False)
                note.user = request.user
                note.show = show
                note.save()
                return redirect('note_detail', note_pk=note.pk), count
        else:
            messages.warning(request, 'You already created a note for this show')
            form = NewNoteForm()
            return render(request, 'lmn/notes/new_note.html', {'form': form, 'show': show})
    else:
        form = NewNoteForm()
        return render(request, 'lmn/notes/new_note.html', {'form': form, 'show': show})

    return render(request, 'lmn/notes/new_note.html' , { 'form': form , 'show': show })


def latest_notes(request):
    notes = Note.objects.all().order_by('-posted_date')[:20]   # the 20 most recent notes
    return render(request, 'lmn/notes/note_list.html', { 'notes': notes })


def notes_for_show(request, show_pk): 
    # Notes for show, most recent first
    notes = Note.objects.filter(show=show_pk).order_by('-posted_date')
    show = Show.objects.get(pk=show_pk)  
    return render(request, 'lmn/notes/note_list.html', { 'show': show, 'notes': notes })


def note_detail(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)
    return render(request, 'lmn/notes/note_detail.html' , { 'note': note })


# Function to see if the note already exists
def note_already_exist(show_pk,user_pk):
    notes_list = Note.objects.filter(show=show_pk).order_by('-posted_date')
    notes_creator = []
    for note in notes_list:
        notes_creator.append(note.user.pk)
    if user_pk in notes_creator:
        return True
    else:
        return False