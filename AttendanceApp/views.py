from django.shortcuts import render


def initiate_lecture(request):

    return render(request, "AttendanceApp/Initiate_lecture.html")