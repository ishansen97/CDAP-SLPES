from django.shortcuts import render
from django.http import HttpResponse


# Create your views here.
def first(request):
    return HttpResponse('<h1>Hello Attendance App</h1>')
