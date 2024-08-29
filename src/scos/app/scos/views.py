"""
Views for the scos app.
"""

import os
import codecs
from importlib import import_module
import json
import yaml

from django.http import HttpResponse
from django.template import loader
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)
from django.contrib.auth.models import User

from .utils.scos_api import (
    scos_connection_check,
    scos_get_courses,
    scos_get_rightholders,
    scos_get_platforms,
    scos_partners_dict,
    scos_get_course,
    scos_post_course,
    scos_put_course,
)

from .utils.course import (
    CourseInfo,
    get_course_key,
    get_course_info,
)

from .utils.user import (
    get_course_enrollments,
)



CONFIG_FILE = os.environ["CMS_CFG"]
with codecs.open(CONFIG_FILE, encoding="utf-8") as f:
    __config__ = yaml.safe_load(f)
    SCOS_BASE_URL = __config__["SCOS_BASE_URL"]
    SCOS_X_CN_UUID = __config__["SCOS_X_CN_UUID"]
    SCOS_PARTNER_ID = __config__["SCOS_PARTNER_ID"]

SETTINGS = import_module(os.environ["DJANGO_SETTINGS_MODULE"])
LMS_BASE_URL = SETTINGS.LMS_BASE
HTTPS = SETTINGS.HTTPS
LOGIN_URL = SETTINGS.LOGIN_URL

if HTTPS == "on":
    LMS_URL = f"https://{LMS_BASE_URL}/"
elif HTTPS == "off":
    LMS_URL = f"http://{LMS_BASE_URL}/"

common_context = {
    "scos_connection_check": scos_connection_check(),
    "scos_base_url": SCOS_BASE_URL,
    "scos_partner_id": SCOS_PARTNER_ID,
}

def is_staff_check(user: User) -> bool:
    '''
    Проверка наличия у пользователя статуса персонала
    '''
    return user.is_staff



@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def scos(request) -> HttpResponse:
    template = loader.get_template("scos/scos.html")
    scos_platform = scos_partners_dict(scos_get_platforms())[SCOS_PARTNER_ID]
    context = {
        "scos_platform": scos_platform,
    }
    context.update(common_context)
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_all(request) -> HttpResponse:
    template = loader.get_template("scos/course/all.html")
    scos_courses = scos_get_courses()
    scos_rightholders = scos_partners_dict(scos_get_rightholders())
    scos_platform = scos_partners_dict(scos_get_platforms())[SCOS_PARTNER_ID]
    for scos_course in scos_courses["results"]:
        scos_course.update(
            {
                "institution_short_title": scos_rightholders\
                    [scos_course["institution_id"]]["short_title"],
            }
        )
    context = {
        "scos_courses": scos_courses,
        "scos_platform": scos_platform,
    }
    context.update(common_context)
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_add(request) -> HttpResponse:
    template = loader.get_template("scos/course/add.html")
    course_url: str = request.GET.get("course_url")
    if course_url is None:
        context = {}
    else:
        course_key = get_course_key(course_url)
        course_info: CourseInfo = get_course_info(course_key)
        context = {
            "course_url": course_url,
            "course_json": course_info.json(),
            "course": course_info.dictionary(),
        }
    context.update(common_context)
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_update(request, global_id) -> HttpResponse:
    template = loader.get_template("scos/course/update.html")
    scos_course = scos_get_course(global_id)
    course_url = scos_course.get("external_url")
    course_key = get_course_key(course_url)
    course_info = get_course_info(course_key)
    context = {
        "global_id": global_id,
        "course_json": course_info.json(),
        "course": course_info.dictionary(),
    }
    context.update(common_context)
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_send(request, global_id: str = None) -> HttpResponse:
    if request.method == "POST":
        course_info = json.loads(request.body)
        if global_id is None:
            scos_response = scos_post_course(course_info)
            return HttpResponse(json.dumps(scos_response))
        scos_response = scos_put_course(course_info, global_id)
        return HttpResponse(json.dumps(scos_response))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course(request, global_id) -> HttpResponse:
    template = loader.get_template("scos/course/course.html")
    context = {
        "global_id": global_id,
        "scos_course": scos_get_course(global_id),
    }
    context.update(common_context)
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def user_courses(request) -> HttpResponse:
    template = loader.get_template("scos/user/courses.html")
    scos_courses = scos_get_courses()
    scos_rightholders = scos_partners_dict(scos_get_rightholders())
    scos_platform = scos_partners_dict(scos_get_platforms())[SCOS_PARTNER_ID]
    for scos_course in scos_courses["results"]:
        scos_course.update(
            {
                "institution_short_title": scos_rightholders\
                    [scos_course["institution_id"]]["short_title"],
                "session_id": get_course_key(
                    scos_get_course(scos_course["global_id"])["external_url"]\
                )
            }
        )
    context = {
        "scos_courses": scos_courses,
        "scos_platform": scos_platform,
    }
    context.update(common_context)
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def user_course(request, global_id) -> HttpResponse:
    template = loader.get_template("scos/user/course.html")
    course_id = get_course_key(scos_get_course(global_id)["external_url"])
    enrollments = get_course_enrollments(course_id)
    context = {
        "global_id": global_id,
        "course_id": course_id,
        "enrollments": enrollments,
    }
    context.update(common_context)
    return HttpResponse(template.render(context, request))
