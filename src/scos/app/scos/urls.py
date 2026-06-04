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
    course_status,
    course_check,
    course_update,
    course_check_id,
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
    path("course/status/", course_status, name="course_status"),
    path("course/check/", course_check, name="course_check"),
    path("course/check_id/", course_check_id, name="course_check_id"),
    path("course/<str:global_id>/", course, name="course"),
    path("user/courses/", user_courses, name="user_courses"),
    path("user/course/<str:global_id>/", user_course, name="user_course"),
]
