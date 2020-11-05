from django.shortcuts import render
from django.http.response import StreamingHttpResponse
from AttendanceApp.camera import IPWebCam


def initiate_lecture(request):

    return render(request, "AttendanceApp/Initiate_lecture.html")

def gen(camera):
	while True:
		frame = camera.get_frame()
		yield (b'--frame\r\n'
				b'Content-Type: image/jpeg\r\n\r\n' + frame + b'\r\n\r\n')

def webcam_feed(request):
	return StreamingHttpResponse(gen(IPWebCam()),
					content_type='multipart/x-mixed-replace; boundary=frame')