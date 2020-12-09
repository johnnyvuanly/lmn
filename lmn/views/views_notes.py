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
    notes = Note.objects.filter(user=request.user).filter(show=show_pk).order_by('-posted_date') # Display user's notes for specific show, sorted by posted date

    return render(request, 'lmn/notes/note_list.html', { 'show': show, 'notes': notes })

@login_required
def note_detail(request, note_pk):

    note = get_object_or_404(Note, pk=note_pk)
    return render(request, 'lmn/notes/note_detail.html' , { 'note': note })

    
@login_required
def delete_notes(request, note_pk):

    """If this is a note user request, the user clicked the Delete button
    in the form. Delete note to the 
    database, and redirect to this same page.

    If note is not valid, display an url response forbidden. 
    """
    note = get_object_or_404(Note, pk=note_pk) 
    if note.user == request.user:
        note.delete() # Delete to the database
        return redirect('venue_list')
    else:
        return HttpResponseForbidden()

@login_required
def edit_notes(request, note_pk):

    """User requests to edit notes by clicking on Edit button.
    User with valid primary key can edit notes in database
    and redirect to starting page. 

    Whereas, invalid primary key will show forbidden information.
    """
    note = get_object_or_404(Note, pk=note_pk) # Return error code and primary key if note not found
    
    # Does this note belong to the current user?
    if note.user != request.user:
        return HttpResponseForbidden()
    
    # is this a GET request (showdata + form), or a POST request (update Note object)?
    # if POST request, validate form data and update.
    if request.method == 'POST':
        form = NewNoteForm(request.POST, instance=note)
        
        if form.is_valid(): # confirm form
            form.save() 
            messages.info(request, 'Note information update!')
        else:
            messages.error(request, form.errors)
        
        return redirect('note_detail', note_pk=note_pk)
    
    else:
    # If GET request, show Note information and form.
    # If Note is edited, show form; if note is not edited, no form
        if note:
            form = NewNoteForm(instance=note)# get new form
            return render(request, 'lmn/notes/note_edit.html' , { 'form': form, 'note': note})
        
        else:
            return render(request, 'lmn/notes/note_edit.html' ,  { 'form': form})
    
