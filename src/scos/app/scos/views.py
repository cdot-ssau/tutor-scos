"""
Views for the scos app.
"""

import json

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
    scos_get_moderation_status,
    scos_get_status
)

from .utils.course import (
    CourseInfo,
    get_course_key,
    get_course_info,
)

from .utils.user import (
    get_course_enrollments,
)

from .utils.config import (
    SCOS_BASE_URL,
    SCOS_PARTNER_ID,
    LMS_URL,
)



class CommonContext(dict):

    def __init__(self):
        super().__init__()
        self.update(
            {
                "scos_base_url": SCOS_BASE_URL,
                "scos_partner_id": SCOS_PARTNER_ID,
                "scos_connection_check": scos_connection_check(),
            }
        )

def is_staff_check(user: User) -> bool:
    """
    Проверка наличия у пользователя статуса персонала
    """
    return user.is_staff



@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def scos(request) -> HttpResponse:
    template = loader.get_template("scos/scos.html")
    context = CommonContext()
    platforms = scos_get_platforms()
    if platforms:
        scos_platform = scos_partners_dict(platforms)[SCOS_PARTNER_ID]
    else:
        scos_platform = None
    context.update(
        {
            "scos_platform": scos_platform
        }
    )
    print(context)
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_all(request) -> HttpResponse:
    template = loader.get_template("scos/course/all.html")
    context = CommonContext()
    scos_courses = scos_get_courses()
    scos_rightholders = scos_partners_dict(scos_get_rightholders())
    scos_platform = scos_partners_dict(scos_get_platforms())[SCOS_PARTNER_ID]
    for scos_course in scos_courses["results"]:
        scos_course.update(
            {
                "institution_short_title": scos_rightholders[
                    scos_course["institution_id"]]["short_title"],
                "moderation_status": scos_get_moderation_status(
                    scos_course["global_id"])["status"],
                "status": scos_get_status(scos_course["global_id"])["status"]
            }
        )
    context.update(
        {
            "scos_courses": scos_courses,
            "scos_platform": scos_platform,
        }
    )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_add(request) -> HttpResponse:
    template = loader.get_template("scos/course/add.html")
    context = CommonContext()
    course_url: str = request.GET.get("course_url")
    if course_url is not None:
        course_key = get_course_key(course_url)
        course_info: CourseInfo = get_course_info(course_key)
        if course_info:
            context.update(
                {
                    "course_url": course_url,
                    "course_json": course_info.json(),
                    "course": course_info.dictionary(),
                }
            )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_update(request, global_id) -> HttpResponse:
    template = loader.get_template("scos/course/update.html")
    context = CommonContext()
    scos_course = scos_get_course(global_id)
    course_url = scos_course.get("external_url")
    course_key = get_course_key(course_url)
    course_info = get_course_info(course_key)
    context.update(
        {
            "global_id": global_id,
            "course_json": course_info.json(),
            "course": course_info.dictionary(),
        }
    )
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
    context = CommonContext()
    context.update(
        {
            "global_id": global_id,
            "scos_course": scos_get_course(global_id),
            "moderation_status": scos_get_moderation_status(global_id)["status"],
            "status": scos_get_status(global_id)["status"]
        }
    )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def user_courses(request) -> HttpResponse:
    template = loader.get_template("scos/user/courses.html")
    context = CommonContext()
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
    context.update(
        {
            "scos_courses": scos_courses,
            "scos_platform": scos_platform,
        }
    )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def user_course(request, global_id) -> HttpResponse:
    template = loader.get_template("scos/user/course.html")
    context = CommonContext()
    course_id = get_course_key(scos_get_course(global_id)["external_url"])
    enrollments = get_course_enrollments(course_id)
    context.update(
        {
            "global_id": global_id,
            "course_id": course_id,
            "enrollments": enrollments,
        }
    )
    return HttpResponse(template.render(context, request))
