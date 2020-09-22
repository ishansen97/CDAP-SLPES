from django.urls import path, re_path, include
from django.conf.urls import url
from rest_framework import routers
from . import views
# from . import api

router = routers.DefaultRouter()
# router.register(r'^register', views.RegisterViewSet)
# router.register(r'^createImage', views.ImageViewSet)

urlpatterns = [
    path('/summarization', views.summarization),


    # routers
    # path('', include(router.urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]
from rest_framework.urlpatterns import format_suffix_patterns
