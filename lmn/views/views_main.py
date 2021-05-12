from django.shortcuts import render

""" Run the homepage when the application starts """

def homepage(request):
    return render(request, 'lmn/home.html')

