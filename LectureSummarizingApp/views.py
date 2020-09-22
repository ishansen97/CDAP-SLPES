from django.shortcuts import render

# Create your views here.

def summarization(request):

    return render(request, "LectureSummarizingApp/summarization.html")