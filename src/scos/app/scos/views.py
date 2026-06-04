"""
Views for the scos app.
"""

import logging
import json
from typing import Any
from urllib.parse import urlparse
from functools import wraps

from django.http import (
    JsonResponse,
    HttpResponse,
    HttpResponseServerError,
    HttpResponseBadRequest,
    HttpResponseNotFound,
)
from django.views.decorators.http import require_http_methods
from django.shortcuts import redirect
from django.template import loader
from django.contrib.auth.decorators import (
    login_required,
    user_passes_test,
)
from django.contrib.auth.models import User
from django.core.cache import cache

from .utils.scos_api import (
    get_scos_course,
    scos_connection_check,
    scos_get_courses,
    scos_get_rightholders,
    scos_get_platforms,
    scos_partners_dict,
    scos_get_course,
    scos_post_course,
    scos_put_course,
    scos_get_moderation_status,
    scos_get_status,
    scos_put_status
)

from .utils.course import (
    CourseInfo,
    get_course_key,
    get_course_info,
    get_course_info_from_scos,
)

from .utils.user import (
    get_course_enrollments,
)

from .utils.config import (
    SCOS_BASE_URL,
    SCOS_PARTNER_ID,
    LMS_URL,
)



LOGGER = logging.getLogger(__name__)



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

def check_domain(url: str) -> bool:
    """
    Проверка домена в адресе url на соответствие домену платформы
    """
    try:
        parsed_url = urlparse(url)
        domain = parsed_url.netloc.split(':')[0].lower()
        parsed_lms = urlparse(LMS_URL if '://' in LMS_URL else f"https://{LMS_URL}")
        lms_domain = parsed_lms.netloc.split(':')[0].lower()
        return domain == lms_domain
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error(
            "СЦОС views. %s. %s",
            "Error processing url domain",
            exception
        )
        return False

def allow_cors(view_function):
    """
    Добавление заголовка CORS к ответу
    """
    @wraps(view_function)
    def _wrapped_view(request, *args, **kwargs):
        origin = request.headers.get("Origin", "*")
        if origin == "*":
            LOGGER.error("СЦОС views. Missing Origin header.")

        if request.method == "OPTIONS":
            response = JsonResponse({})
            response["Access-Control-Allow-Methods"] = "GET, OPTIONS"
            response["Access-Control-Allow-Headers"] = "Content-Type"
            response["Access-Control-Allow-Origin"] = origin
            return response

        if origin != "*":
            if not check_domain(origin):
                LOGGER.error("СЦОС views. Unauthorized cross-origin domain: %s", origin)
                return HttpResponseBadRequest("Unauthorized cross-origin domain")

        try:
            response = view_function(request, *args, **kwargs)
        except Exception as exception: # pylint: disable=broad-except
            LOGGER.error("СЦОС views. %s", exception)
            response = HttpResponseServerError("Internal server error.")

        response["Access-Control-Allow-Origin"] = origin
        return response
    return _wrapped_view

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def scos(request) -> HttpResponse:
    template = loader.get_template("scos/scos.html")
    context = CommonContext()
    try:
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
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)
        context.update(
            {
                "error": "При формировании страницы возникла ошибка, проверьте лог-файл tutor",
            }
        )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_all(request) -> HttpResponse:
    template = loader.get_template("scos/course/all.html")
    context = CommonContext()
    try:
        scos_courses = scos_get_courses()
        scos_rightholders = scos_partners_dict(scos_get_rightholders())
        scos_platforms = scos_partners_dict(scos_get_platforms())
        scos_platform = scos_platforms.get("SCOS_PARTNER_ID")
        for scos_course in scos_courses["results"]:
            scos_course.update(
                {
                    "institution_short_title": scos_rightholders[
                        scos_course["institution_id"]]["short_title"],
                }
            )
        context.update(
            {
                "scos_courses": scos_courses,
                "scos_platform": scos_platform,
            }
        )
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)
        context.update(
            {
                "error": "При формировании страницы возникла ошибка, проверьте лог-файл tutor",
            }
        )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_add(request) -> HttpResponse:
    template = loader.get_template("scos/course/add.html")
    context = CommonContext()
    try:
        course_url = request.GET.get("course_url")
        if course_url is not None:
            course_key = get_course_key(course_url)
            course_info: CourseInfo = get_course_info(course_key)
            if course_info:
                context.update(
                    {
                        "course_url": course_url,
                        "course": course_info.dictionary_json(),
                    }
                )
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)
        context.update(
            {
                "error": "При формировании страницы возникла ошибка, проверьте лог-файл tutor",
            }
        )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_update(request, global_id) -> HttpResponse:
    template = loader.get_template("scos/course/update.html")
    context = CommonContext()
    try:
        scos_course = scos_get_course(global_id)
        course_url = request.GET.get("course_url")
        if course_url is None:
            course_url = scos_course.get("external_url")
        course_key = get_course_key(course_url)
        course_info = get_course_info(course_key)
        scos_course_info = get_course_info_from_scos(scos_course)
        if course_info is None:
            course_info = scos_course_info
        else:
            course_info.institution.value = scos_course_info.institution.value
        course_info.business_version.value = int(scos_course_info.business_version.value) + 1
        context.update(
            {
                "global_id": global_id,
                "course": course_info.dictionary_json(),
            }
        )
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)
        context.update(
            {
                "error": "При формировании страницы возникла ошибка, проверьте лог-файл tutor",
            }
        )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
@require_http_methods(["POST"])
def course_send(request, global_id = None) -> JsonResponse:
    try:
        course_info = json.loads(request.body)
        if global_id is None:
            scos_response = scos_post_course(course_info)
            return JsonResponse(scos_response)
        scos_response = scos_put_course(course_info, global_id)
        return JsonResponse(scos_response)
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
@require_http_methods(["GET", "PUT"])
def course_status(request) -> Any:
    global_id: str = request.GET.get("global_id", "")
    if not global_id:
        LOGGER.error("СЦОС views. Missing global_id parameter.")
        return HttpResponseBadRequest("Missing query parameters.")

    if request.method == "GET":
        try:
            scos_response = scos_get_status(global_id)
            if scos_response is None:
                LOGGER.error("СЦОС views. View aborted because API call returned None.")
                return HttpResponseServerError("External API error.")
            return HttpResponse(scos_response, content_type="text/plain")
        except Exception as exception: # pylint: disable=broad-except
            LOGGER.error("СЦОС views. %s", exception)
            return HttpResponseServerError("Internal server error.")

    elif request.method == "PUT":
        is_active: str = request.GET.get("is_active", "")
        if not is_active:
            LOGGER.error("СЦОС views. Missing is_active parameter.")
            return HttpResponseBadRequest("Missing query parameters.")
        try:
            scos_response = scos_put_status(global_id, bool(int(is_active)))
            if scos_response is None:
                LOGGER.error("СЦОС views. View aborted because API call returned None.")
                return HttpResponseServerError("External API error.")
            return JsonResponse(scos_response)
        except Exception as exception: # pylint: disable=broad-except
            LOGGER.error("СЦОС views. %s", exception)
            return HttpResponseServerError("Internal server error.")

@require_http_methods(["GET", "OPTIONS"])
@allow_cors
def course_check(request) -> JsonResponse:
    course_url = request.GET.get("course_url", "")
    if not course_url:
        LOGGER.error("СЦОС views. СЦОС widget view. Missing course_url parameter.")
        return HttpResponseBadRequest("Missing query parameters")

    if not check_domain(course_url):
        LOGGER.error("СЦОС views. СЦОС widget view. Parameter domain mismatch.")
        return HttpResponseBadRequest("Parameter domain mismatch")

    course_key = get_course_key(course_url)
    if not course_key:
        LOGGER.error("СЦОС views. СЦОС widget view. No valid course key in url.")
        return HttpResponseServerError("Internal server error")

    cache_key = f"scos_widget_data_{course_key}"
    cached_api_response = cache.get(cache_key)

    try:
        if cached_api_response:
            api_response = cached_api_response
        else:
            scos_course = get_scos_course(course_key)
            api_response = {
                "has_data": scos_course is not None,
                "data": scos_course
            }
            cache.set(cache_key, api_response, timeout=300)
        if api_response["has_data"]:
            if SCOS_BASE_URL == "https://test.online.edu.ru":
                widget_url = "https://test.online.edu.ru"
            else:
                widget_url = "https://online.edu.ru"
            return JsonResponse(
                {
                    "scos": {
                        "widget_url": widget_url,
                        "course_id": api_response["data"]["global_id"],
                        "course_version": api_response["data"]["business_version"],
                    }
                }
            )
        else:
            return HttpResponseNotFound("Course not found on SCOS")
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. SCOS widget view. %s", exception)
        return HttpResponseServerError("Internal server error")

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course(request, global_id) -> HttpResponse:
    template = loader.get_template("scos/course/course.html")
    context = CommonContext()
    try:
        context.update(
            {
                "global_id": global_id,
                "scos_course": scos_get_course(global_id),
                "moderation_status": scos_get_moderation_status(global_id)["status"],
                "status": scos_get_status(global_id)
            }
        )
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)
        context.update(
            {
                "error": "При формировании страницы возникла ошибка, проверьте лог-файл tutor",
            }
        )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def course_check_id(request) -> HttpResponse:
    try:
        course_id = request.GET.get("course_id")
        scos_course = scos_get_course(course_id)
        if scos_course:
            return redirect("scos:course", global_id = course_id)
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)
    return HttpResponse("Курс с таким ID не найден")

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def user_courses(request) -> HttpResponse:
    template = loader.get_template("scos/user/courses.html")
    context = CommonContext()
    try:
        scos_courses = scos_get_courses()
        scos_rightholders = scos_partners_dict(scos_get_rightholders())
        scos_platforms = scos_partners_dict(scos_get_platforms())
        scos_platform = scos_platforms.get("SCOS_PARTNER_ID")
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
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)
        context.update(
            {
                "error": "При формировании страницы возникла ошибка, проверьте лог-файл tutor",
            }
        )
    return HttpResponse(template.render(context, request))

@login_required
@user_passes_test(is_staff_check, login_url=LMS_URL)
def user_course(request, global_id) -> HttpResponse:
    template = loader.get_template("scos/user/course.html")
    context = CommonContext()
    try:
        scos_course = scos_get_course(global_id)
        course_id = get_course_key(scos_course["external_url"])
        enrollments = get_course_enrollments(course_id)
        context.update(
            {
                "global_id": global_id,
                "course_id": course_id,
                "enrollments": enrollments,
            }
        )
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС views. %s", exception)
        context.update(
            {
                "error": "При формировании страницы возникла ошибка, проверьте лог-файл tutor",
            }
        )
    return HttpResponse(template.render(context, request))
