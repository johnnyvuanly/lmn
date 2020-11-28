from django.shortcuts import render, redirect

from ..models import Show
from ..forms import NewShowForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout
from django.core.exceptions import ValidationError
from django.contrib import messages

@login_required
def add_show(request):

    if request.method == 'POST':
        #create new show
        new_show_form = NewShowForm(request.POST)
        if new_show_form.is_valid():
            try:
                show = new_show_form.save(commit=False)
                show.user = request.user
                if not is_unique(request, show):
                    raise ValidationError('Show is not unique')       
                show.save()
                return redirect('homepage')
            except ValidationError:
                messages.warning(request, 'You already added that show.')
            
        messages.warning(request, 'Please check data entered.')
        return render(request, 'lmn/show_add.html', {'new_show_form': new_show_form})

    new_show_form = NewShowForm()
    return render(request, 'lmn/show_add.html', {'new_show_form': new_show_form})

def is_unique(request, show):
    try:
        if Show.objects.filter(show_date=show.show_date, show_time=show.show_time, artist=show.artist, venue=show.venue).exists():
            return False
        return True
    except Exception as e:
        messages.warning(request, e)