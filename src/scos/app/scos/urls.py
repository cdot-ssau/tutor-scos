"""
URLs for the scos app.
"""

from django.urls import path

from .views import (
    scos,
    course_all,
    course,
    course_add,
    course_send,
    course_update,
    user_courses,
    user_course
)

app_name = 'cms.djangoapps.scos'

urlpatterns = [
    path("", scos, name="scos"),
    path("course/all/", course_all, name="course_all"),
    path("course/add/", course_add, name="course_add"),
    path("course/update/<str:global_id>/", course_update, name="course_update"),
    path("course/send/$", course_send, name="course_send"),
    path("course/send/<str:global_id>/$", course_send, name="course_send"),
    path("course/<str:global_id>/", course, name="course"),
    path("user/courses/", user_courses, name="user_courses"),
    path("user/course/<str:global_id>/", user_course, name="user_course"),
]
