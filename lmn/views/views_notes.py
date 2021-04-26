from django.core.checks import messages
from django.http.request import HttpRequest
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
        form = NewNoteForm(request.POST,)
        if form.is_valid():
            note = form.save(commit=False)
            note.user = request.user
            note.show = show
            note.save()
            return redirect('note_detail', note_pk=note.pk)

    else:
        form = NewNoteForm()

    return render(request, 'lmn/notes/new_note.html' , { 'form': form , 'show': show })


def latest_notes(request):
    notes = Note.objects.all().order_by('-posted_date')[:20]   # the 20 most recent notes
    return render(request, 'lmn/notes/note_list.html', { 'notes': notes })


def notes_for_show(request, show_pk): 
    # Notes for show, most recent first
    notes = Note.objects.filter(show=show_pk).order_by('-posted_date')
    show = Show.objects.get(pk=show_pk)  
    return render(request, 'lmn/notes/note_list.html', { 'show': show, 'notes': notes })


@login_required
def change_notes(request, note_pk):
    notes = get_object_or_404(Note, pk=note_pk)

    # Find out if this note belongs to the current user
    if notes.user != request.user:
        return HttpResponseForbidden()
    
    # If POST request
    if request.method == 'POST':
        form = NewNoteForm(request.POST, request.FILES, instance=notes)
        if form.is_valid():
            form.save()
            messages.info(request, 'Note Updated!')
        else:
            messages.error(request, form.errors)
        return redirect('note_detail', note_pk=note_pk)

    # If GET request
    else:
        review_form = NewNoteForm(instance=notes)
        return render(request, 'lmn/notes/edit_notes.html', {'note': notes, 'review_form': review_form})

@login_required
def delete_note(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)
    if note.user == request.user:
        note.delete()
        messages.info(request, 'Note Deleted Successfully')
    else:
        messages.info(request, 'Unable to delete')
    return redirect('my_user_profile')




def note_detail(request, note_pk):
    note = get_object_or_404(Note, pk=note_pk)
    return render(request, 'lmn/notes/note_detail.html' , { 'note': note })


