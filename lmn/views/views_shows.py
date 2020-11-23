from django.shortcuts import render, redirect

from ..models import Show
from ..forms import NewShowForm

from django.contrib.auth.decorators import login_required
from django.contrib.auth.models import User
from django.contrib.auth import authenticate, login, logout

@login_required
def add_show(request):

    if request.method == 'POST':
        #create new show
        form = NewShowForm(request.POST)
        show = form.save(commit=False)
        show.user = request.user
        if form.is_valid():
            show.save()
            return redirect('homepage')

    new_show_form = NewShowForm()
    return render(request, 'lmn/show_add.html', {'new_show_form': new_show_form})