
"""

this file will contain the function-based views where each function will render its
corresponding view (in other words, the HTML file)

each function will accept one parameter

params:
    request - this is the HTTP request sent from the frontend

returns:
    render
    ------
    :params
        request: the HTTP request received
        template_name: path of the HTML template, relative the location of this file
        context: the context that needs to be passed into the template


"""



from django.shortcuts import render, redirect
from django.contrib.auth import (
    authenticate,
    login,
    logout,
)
from django.contrib.auth.decorators import login_required

from . serializers import *
from . forms import *
import os
import datetime as d
from datetime import datetime

from apscheduler.schedulers.background import BackgroundScheduler
from apscheduler.triggers.date import DateTrigger
from apscheduler.jobstores.mongodb import MongoDBJobStore



# Create your views here.

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


####### VIEWS ######
@login_required(login_url='/user-direct')
def hello(request):

    try:
        username = request.user.username
        # retrieve the lecturer
        lecturer = request.session['lecturer']

        user_type = request.session['user_type']

        print('user_type: ', user_type)

        print('request type: ', type(request))

        # test the scheduler
        # test_scheduler()


        # retrieve the lecturer's timetable slots
        lecturer_timetable = FacultyTimetable.objects.filter()

        # serialize the timetable
        lecturer_timetable_serialized = FacultyTimetableSerializer(lecturer_timetable, many=True)


        lecturer_details = []

        # loop through the serialized timetable
        for timetable in lecturer_timetable_serialized.data:

            # retrieve daily timetable
            daily_timetable = timetable['timetable']

            # loop through the daily timetable
            for day_timetable in daily_timetable:
                date = ''
                lecture_index = 0

                # loop through each timeslots
                for slots in day_timetable:

                    if slots == "date":
                        date = day_timetable[slots]


                    elif slots == "time_slots":
                        slot = day_timetable[slots]

                        # loop through each slot
                        for lecture in slot:

                            # check whether the lecturer is the current lecturer
                            if lecturer == lecture['lecturer']['id']:
                                lecturer_lecture_details = {}
                                lecturer_lecture_details['date'] = date
                                lecturer_lecture_details['start_time'] = lecture['start_time']
                                lecturer_lecture_details['end_time'] = lecture['end_time']
                                lecturer_lecture_details['subject_name'] = lecture['subject']['name']
                                lecturer_lecture_details['index'] = lecture_index
                                lecturer_lecture_details['lecturer'] = lecture['lecturer']['id']

                                # append to the lecturer_details
                                lecturer_details.append(lecturer_lecture_details)

                            # increment the index
                            lecture_index += 1

        # sorting the dates in lecturer_details list
        # for details in lecturer_details:
        lecturer_details.sort(key=lambda date: datetime.strptime(str(date['date']), "%Y-%m-%d"), reverse=True)


        obj = {'Message': 'Student and Lecturer Performance Enhancement System', 'username': username}
        folder = os.path.join(BASE_DIR, os.path.join('static\\FirstApp\\videos'))
        videoPaths = [os.path.join(folder, file) for file in os.listdir(folder)]
        videos = []
        durations = []

        context = {'object': obj, 'Videos': videos, 'durations': durations, 'template_name': 'FirstApp/template.html', 'lecturer_details': lecturer_details, "lecturer": lecturer}
        return render(request, 'FirstApp/Home.html', context)

    # in case of keyerror exception
    except KeyError as exc:
        return redirect('/401')

    except Exception as exc:
        print('exception: ', exc)
        return redirect('/500')

# this method will handle 404 error page
def view404(request):
    return render(request, 'FirstApp/404.html')

# this page will handle 401 error page
def view401(request):
    return render(request, 'FirstApp/401.html')


@login_required(login_url='/user-direct')
def gaze(request):
    try:

        # retrieving data from the db
        lecturer = request.session['lecturer']
        lecturer_subjects = LecturerSubject.objects.filter(lecturer_id_id=lecturer)
        lec_sub_serilizer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        subject_list = []

        subjects = lec_sub_serilizer.data[0]['subjects']

        for sub in subjects:
            subject = Subject.objects.filter(id=sub)
            subject_serialized = SubjectSerializer(subject, many=True)

            subject_list.append(subject_serialized.data)


    # handling the keyError
    except KeyError as exc:
        return redirect('/401')

    # handling the general exceptions
    except Exception as exc:
        return redirect('/500')

    return render(request, "FirstApp/gaze.html",
                  {"lecturer_subjects": lecturer_subjects, "subjects": subject_list, "lecturer": lecturer})



def loginForm(request):
    return render(request, 'FirstApp/login.html')


def template(request):
    obj = {'Message': 'Student and Lecturer Performance Enhancement System'}
    return render(request, 'FirstApp/template.html', {'template_name': 'FirstApp/template.html', 'object': obj})


# displaying video results
@login_required(login_url='/user-direct')
def video_result(request):
    try:

        # retrieving data from the db
        lecturer = request.session['lecturer']
        to_do_lecture_list = []
        due_lecture_list = []

        lecturer_videos = LectureVideo.objects.filter(lecturer_id=lecturer)
        serializer = LectureVideoSerializer(lecturer_videos, many=True)

        data = serializer.data

        print('data length: ', len(data))

        # iterate through the existing lecture videos for the lecturer
        for video in data:
            video_id = video['id']
            date = video['date']
            subject = video['subject']['id']
            # check whether the video id exist in the Activity Recognition table
            lec_activity = LectureActivity.objects.filter(lecture_video_id_id=video_id).exists()

            print('lecture activity existence: ', lec_activity)

            if lec_activity == False:
                to_do_lecture_list.append({
                    "lecturer": lecturer,
                    "date": date,
                    "subject": subject,
                    "video_id": video['id'],
                    "video_name": video['video_name']
                })

        # once the lectures that needs to be processed are found out, extract the corresponding timetable details
        # retrieve the lecturer's timetable slots
        lecturer_timetable = FacultyTimetable.objects.filter()

        # serialize the timetable
        lecturer_timetable_serialized = FacultyTimetableSerializer(lecturer_timetable, many=True)

        # loop through the serialized timetable
        for timetable in lecturer_timetable_serialized.data:

            # retrieve daily timetable
            daily_timetable = timetable['timetable']

            # loop through the daily timetable
            for day_timetable in daily_timetable:

                # print('day timetable" ', day_timetable)

                # loop through the to-do lecture list
                for item in to_do_lecture_list:
                    isDate = item['date'] == str(day_timetable['date'])

                    # print('item date: ', item['date'])
                    # print('timetable date: ', str(day_timetable['date']))

                    # isLecturer = item['lecturer'] ==
                    # check for the particular lecture on the day
                    if isDate:
                        slots = day_timetable['time_slots']


                        # loop through the slots
                        for slot in slots:
                            # check for the lecturer and subject
                            isLecturer = item['lecturer'] == slot['lecturer']['id']
                            isSubject = item['subject'] == slot['subject']['id']

                            print('item lecturer: ', item['lecturer'])
                            print('timetable lecturer: ', slot['lecturer']['id'])

                            print('item subject: ', item['subject'])
                            print('timetable subject: ', slot['subject']['id'])

                            if isLecturer & isSubject:
                                obj = {}
                                obj['date'] = item['date']
                                obj['subject'] = slot['subject']['subject_code']
                                obj['subject_name'] = slot['subject']['name']
                                obj['start_time'] = slot['start_time']
                                obj['end_time'] = slot['end_time']
                                obj['video_id'] = item['video_id']
                                obj['video_name'] = item['video_name']

                                # append to the list
                                due_lecture_list.append(obj)

    # handling the keyError
    except KeyError as exc:
        return redirect('/401')

    # handling the general exceptions
    except Exception as exc:
        print('Exception: ', exc)
        return redirect('/500')

    print('due lectures: ', due_lecture_list)

    due_lecture_video_name = due_lecture_list[0]['video_name'] if len(due_lecture_list) > 0 else "Test.mp4"
    # due_lecture_video_name = "Test.mp4"
    print('due lecture video name: ', due_lecture_video_name)

    # check whether there are due lectures or not
    isDue = len(due_lecture_list)

    return render(request, "FirstApp/video_results.html",
                  {"lecturer": lecturer, "due_lectures": due_lecture_list, "due_lecture_video_name": due_lecture_video_name, 'isDue': isDue})


# view for emotion page
@login_required(login_url='/user-direct')
def emotion_view(request):
    try:

        # retrieving data from the db
        lecturer = request.session['lecturer']
        lecturer_subjects = LecturerSubject.objects.filter(lecturer_id_id=lecturer)
        lec_sub_serilizer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        subject_list = []

        subjects = lec_sub_serilizer.data[0]['subjects']

        for sub in subjects:
            subject = Subject.objects.filter(id=sub)
            subject_serialized = SubjectSerializer(subject, many=True)

            subject_list.append(subject_serialized.data)


    # handling the keyError
    except KeyError as exc:
        return redirect('/401')

    # handling the general exceptions
    except Exception as exc:
        return redirect('/500')

    return render(request, "FirstApp/emotion.html",
                  {"lecturer_subjects": lecturer_subjects, "subjects": subject_list, "lecturer": lecturer})


# signing In the user
def loggedInView(request):
    username = "not logged in"
    message = "Invalid Username or Password"
    MyLoginForm = LoginForm(request.POST)

    print('message: ', message)

    try:
        # if the details are valid, let the user log in
        if MyLoginForm.is_valid():
            email = MyLoginForm.cleaned_data.get('email')
            password = MyLoginForm.cleaned_data.get('password')

            user = User.objects.get(email=email)
            lecturer = Lecturer.objects.get(email=email)

            login(request, user)
            # setting up the session
            request.session['lecturer'] = lecturer.id
            request.session['user_type'] = "Lecturer"

            return redirect('/')

        else:
            message = "Please provide correct credntials"
    except Exception as exc:
        print('exception: ', exc)

    return render(request, 'FirstApp/login.html', {'message': message})


# signing out the user
def logoutView(request):

    logout(request)

    return redirect('/user-direct')


# 500 error page
def view500(request):
    return render(request, "FirstApp/500.html")



@login_required(login_url='/user-direct')
def activity(request):
    try:

        # retrieving data from the db
        lecturer = request.session['lecturer']
        lecturer_subjects = LecturerSubject.objects.filter(lecturer_id_id=lecturer)
        lec_sub_serilizer = LecturerSubjectSerializer(lecturer_subjects, many=True)
        subject_list = []

        subjects = lec_sub_serilizer.data[0]['subjects']

        for sub in subjects:
            subject = Subject.objects.filter(id=sub)
            subject_serialized = SubjectSerializer(subject, many=True)

            subject_list.append(subject_serialized.data)


    # handling the keyError
    except KeyError as exc:
        return redirect('/401')

    # handling the general exception
    except Exception as exc:
        print('exception: ', exc)
        return redirect('/500')

    return render(request, "FirstApp/activity.html", {"lecturer_subjects": lecturer_subjects, "subjects": subject_list, "lecturer": lecturer})


def test(request):
    return render(request, "FirstApp/pdf_template.html")


# this method will handle user directing function
def userDirect(request):
    return render(request, "FirstApp/user_direct.html")


# this method will handle user redirection process
def processUserRedirect(request):

    if request.POST:

        user_type = request.POST.get('user_type')

        if user_type == 'admin':
            return redirect('/admin-login')
        elif user_type == 'lecturer':
            return redirect('/login')

    return redirect('/500')


# admin login page
def adminLogin(request):

    return render(request, "FirstApp/admin_login.html")


# this method will process admin login
def processAdminLogin(request):
    username = "not logged in"
    message = "Invalid Username or Password"
    adminLoginForm = AdminLoginForm(request.POST)

    print('message: ', message)

    try:
        # if the details are valid, let the user log in
        if adminLoginForm.is_valid():
            email = adminLoginForm.cleaned_data.get('email')

            user = User.objects.get(email=email)
            admin = Admin.objects.get(email=email)

            login(request, user)
            # setting up the session
            request.session['admin'] = admin.id
            request.session['user_type'] = "Admin"

            return redirect('/lecturer')

        else:
            message = "Please provide correct credntials"
    except Exception as exc:
        print('exception: ', exc)

    return render(request, 'FirstApp/admin_login.html', {'message': message})