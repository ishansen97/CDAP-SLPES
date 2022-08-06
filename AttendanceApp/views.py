from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from AttendanceApp.camera import IPWebCam
from FirstApp.MongoModels import LectureVideo, FacultyTimetable
from FirstApp.serializers import LectureVideoSerializer, FacultyTimetableSerializer

import datetime as d
from datetime import datetime


def initiate_lecture(request):
    lecturer = request.session['lecturer']
    lecturerName = request.session['lecturer-name']

    print(lecturer)
    upcoming_lecture_details = upcoming_lecture_request(lecturer)
    print(upcoming_lecture_details)

    context = {'lecturerId': lecturer, 'lecturerName': lecturerName, 'upcomingLecture': upcoming_lecture_details}
    return render(request, "AttendanceApp/Initiate_lecture.html", context)


def gen(camera):
    while True:
        frame = camera.get_frame()
        yield (b'--frame\r\n'
               b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')


def webcam_feed(request):
    return StreamingHttpResponse(gen(IPWebCam()),
                                 content_type='multipart/x-mixed-replace; boundary=frame')


def upcoming_lecture_request(lecturer):
    cur_date = d.datetime.now().date()
    cur_time = d.datetime.now().time()

    print('lecturer: ', lecturer)

    upcoming_lecture_details = {}

    # retrieve the faculty timetable
    faculty_timetable = FacultyTimetable.objects.all()

    # serialize the timetable
    faculty_timetable_serialized = FacultyTimetableSerializer(faculty_timetable, many=True)

    # get the serialized timetable data
    faculty_timetable_serialized_data = faculty_timetable_serialized.data

    # iterate through the serialized timetable data
    for timetable in faculty_timetable_serialized_data:

        # get the 'timetable' field
        daily_timetable = timetable['timetable']

        # iterate through the 'timetable' field
        for day_timetable in daily_timetable:

            # get the 'time_slots' field for a given day
            time_slots = day_timetable['time_slots']

            # iterate through the time slots
            for time_slot in time_slots:

                # if the lecturer is the currently logged in lecturer
                if lecturer == time_slot['lecturer']['id']:

                    # find the upcoming lecture for the logged-in lecturer
                    if cur_date == day_timetable['date']:

                        # get the start and end times
                        start_time = time_slot['start_time']
                        end_time = time_slot['end_time']

                        start_time_list = str(start_time).split(":")

                        start_time_date = d.datetime.now().replace(hour=int(start_time_list[0]),
                                                                   minute=int(start_time_list[1]),
                                                                   second=int(start_time_list[2]))

                        end_time_list = str(end_time).split(":")

                        end_time_date = d.datetime.now().replace(hour=int(end_time_list[0]),
                                                                 minute=int(end_time_list[1]),
                                                                 second=int(end_time_list[2]))

                        # check for the upcoming time slot
                        if (start_time_date.time() > cur_time):
                            upcoming_lecture_details['eligible_start_time'] = start_time_date.time()
                            upcoming_lecture_details['eligible_end_time'] = end_time_date.time()
                            upcoming_lecture_details['subject_id'] = time_slot['subject']['id']
                            upcoming_lecture_details['subject_name'] = time_slot['subject']['name']
                            upcoming_lecture_details['subject_code'] = time_slot['subject']['subject_code']

    return upcoming_lecture_details

    # lecturer = int(lecturer)
    # lecturer = int(lecturer)
    # cur_date = datetime.datetime.now().date()
    # cur_date = d.datetime.now().date()
    # cur_time = d.datetime.now().time()
    #
    # # upcoming lecture details
    # upcoming_lecture_details = {}
    #
    # eligible_start_time = ''
    # eligible_end_time = ''
    # subject_id = 0
    # subject_name = ''
    # subject_code = ''
    #
    # # retrieve the faculty timetable
    # faculty_timetable = FacultyTimetable.objects.all()
    #
    # # serialize the timetable
    # faculty_timetable_serialized = FacultyTimetableSerializer(faculty_timetable, many=True)
    #
    # # get the serialized timetable data
    # faculty_timetable_serialized_data = faculty_timetable_serialized.data
    #
    # # iterate through the serialized timetable data
    # for timetable in faculty_timetable_serialized_data:
    #
    #     # get the 'timetable' field
    #     daily_timetable = timetable['timetable']
    #
    #     # iterate through the 'timetable' field
    #     for day_timetable in daily_timetable:
    #
    #         # get the 'time_slots' field for a given day
    #         time_slots = day_timetable['time_slots']
    #
    #         # iterate through the time slots
    #         for time_slot in time_slots:
    #
    #             # if the lecturer is the currently logged in lecturer
    #             if lecturer == time_slot['lecturer']['id']:
    #
    #                 # find the upcoming lecture for the logged-in lecturer
    #                 if cur_date == day_timetable['date']:
    #
    #                     # get the start and end times
    #                     start_time = time_slot['start_time']
    #                     end_time = time_slot['end_time']
    #
    #                     start_time_list = str(start_time).split(":")
    #
    #                     start_time_date = d.datetime.now().replace(hour=int(start_time_list[0]),
    #                                                                       minute=int(start_time_list[1]),
    #                                                                       second=int(start_time_list[2]))
    #
    #                     end_time_list = str(end_time).split(":")
    #
    #                     end_time_date = d.datetime.now().replace(hour=int(end_time_list[0]),
    #                                                                     minute=int(end_time_list[1]),
    #                                                                     second=int(end_time_list[2]))
    #
    #                     # check for the upcoming t ime slot
    #                     if (start_time_date.time() > cur_time):
    #                         upcoming_lecture_details['eligible_start_time'] = start_time_date.time()
    #                         upcoming_lecture_details['eligible_end_time'] = end_time_date.time()
    #                         upcoming_lecture_details['subject_id'] = time_slot['subject']['id']
    #                         upcoming_lecture_details['subject_name'] = time_slot['subject']['name']
    #                         upcoming_lecture_details['subject_code'] = time_slot['subject']['subject_code']
    #

    # return upcoming_lecture_details

