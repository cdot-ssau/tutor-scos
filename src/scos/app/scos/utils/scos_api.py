"""
SCOS API utils.

Документация по API СЦОС:
https://tech.online.edu.ru/files/api.pdf - Описание программных интерфейсов
государственной информационной системы "Современная цифровая образовательная
среда", размещенной в информационно-телекоммуникационной сети "Интернет" по
адресу online.edu.ru
"""

import logging
from typing import Any

import requests

from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from .course import (
    get_course_info_from_overview,
)

from .config import (
    SCOS_BASE_URL,
    SCOS_X_CN_UUID,
    SCOS_PARTNER_ID,
    SCOS_HTTPS_PROXY,
)

disable_warnings(InsecureRequestWarning)

LOGGER = logging.getLogger(__name__)

HEADERS_GET = {
    "X-CN-UUID": SCOS_X_CN_UUID,
    "Accept": "application/json",
}
HEADERS = {
    "X-CN-UUID": SCOS_X_CN_UUID,
    "Content-type": "application/json",
    "Accept": "application/json",
}
PROXIES = {}
TIMEOUT = (3.0, 21.0)

if SCOS_HTTPS_PROXY:
    PROXIES.update({"https":SCOS_HTTPS_PROXY})



def scos_connection_check() -> str:
    """
    1. Проверка подключения к API тестового контура ГИС СЦОС
    https://tech.online.edu.ru/files/3_apllication_instructions.pdf
    """
    url = f"{SCOS_BASE_URL}/api/v2/connections/check"
    try:
        response: requests.Response = requests.get(
            url = url,
            headers = HEADERS_GET,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return exception
    return str(response.status_code)

def scos_get_platforms() -> Any:
    """
    3.1.10. Список всех платформ
    """
    url = f"{SCOS_BASE_URL}/api/v2/registry/partners/platforms"
    try:
        response: requests.Response = requests.get(
            url = url,
            headers = HEADERS_GET,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        platforms = response.json()
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return platforms

def scos_get_rightholders() -> Any:
    """
    3.1.11. Список всех Правообладателей
    """
    url = f"{SCOS_BASE_URL}/api/v2/registry/partners/rightholders"
    try:
        response: requests.Response = requests.get(
            url = url,
            headers = HEADERS_GET,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        rightholders = response.json()
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return rightholders

def scos_partners_dict(partners: dict) -> dict:
    """
    Возвращает словарь из списка, ключ - global_id
    """
    try:
        partners = {row["global_id"]: row for row in partners["rows"]}
    except TypeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return partners

def scos_get_courses(**kwargs) -> Any:
    """
    3.1.14. Список онлайн-курсов
    
    Возвращает список онлайн-курсов. Дополнительно можно задать параметры
фильтра для следующих атрибутов: language, institution_id, partner_id,
direction_id, activity_id. По умолчанию используется фильтр по идентификатору
платформы - partner_id.
    """
    url = f"{SCOS_BASE_URL}/api/v2/registry/courses"
    params = {"partner_id": SCOS_PARTNER_ID}
    options: set[str] = {
        "language",
        "institution_id",
        "partner_id",
        "direction_id",
        "activity_id",
    }
    for option in options:
        if option in kwargs:
            params.update(option=kwargs[option])
    try:
        response: requests.Response = requests.get(
            url = url,
            headers = HEADERS_GET,
            proxies = PROXIES,
            verify = False,
            params = params,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        scos_courses = response.json()
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return scos_courses

def scos_get_course(global_id: str) -> Any:
    """
    3.1.15. Получение одного онлайн-курса
    """
    url = f"{SCOS_BASE_URL}/api/v2/registry/courses/{global_id}"
    try:
        response: requests.Response = requests.get(
            url = url,
            headers = HEADERS_GET,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        course_info = response.json()
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return course_info

def scos_post_course(course_info: dict) -> Any:
    """
    3.1.5. Добавление онлайн-курса
    """
    url = f"{SCOS_BASE_URL}/api/v2/registry/courses"
    payload = {
        "partner_id": SCOS_PARTNER_ID,
        "package": {
            "items": [course_info]
        }
    }
    try:
        response: requests.Response = requests.post(
            url = url,
            json = payload,
            headers = HEADERS,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        scos_response = response.json()
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return scos_response

def scos_put_course(course_info: dict, global_id:str) -> Any:
    """
    3.1.6. Обновление онлайн-курса
    """
    url = f"{SCOS_BASE_URL}/api/v2/registry/courses"
    course_info.update({"id": global_id})
    payload = {
        "partner_id": SCOS_PARTNER_ID,
        "package": {
            "items": [course_info]
        }
    }
    try:
        response: requests.Response = requests.put(
            url = url,
            json = payload,
            headers = HEADERS,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        scos_response = response.json()
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return scos_response

def scos_get_moderation_status(global_id:str) -> Any:
    """
    3.1.7. Получение статуса оценки онлайн-курса
    """
    url = f"{SCOS_BASE_URL}/api/v2/registry/courses/moderation_status?course_id={global_id}"
    try:
        response: requests.Response = requests.get(
            url = url,
            headers = HEADERS_GET,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        moderation_status = response.json()
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return moderation_status

def scos_put_status(global_id:str, active:bool) -> Any:
    """
    3.1.8. Изменение состояния онлайн-курса
    """
    if active:
        status = "active"
    else:
        status = "archive"
    url = f"{SCOS_BASE_URL}/api/v2/registry/courses/update_status?" + \
        f"course_id={global_id}&status={status}"
    try:
        response: requests.Response = requests.put(
            url = url,
            headers = HEADERS,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        scos_response = response.json()
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return scos_response

def scos_get_status(global_id:str) -> Any:
    """
    3.1.9. Получение статуса онлайн-курса
    """
    url = f"{SCOS_BASE_URL}/api/v2/registry/courses/status?course_id={global_id}"
    try:
        response: requests.Response = requests.get(
            url = url,
            headers = HEADERS_GET,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        status = response.text
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return status

def scos_post_participation(
        course_id: str,
        session_id: str,
        user_id: str,
        enroll_date: str,
        **kwargs
) -> Any:
    """
    4.1.1.2. Регистрация списка слушателей на курс
    """
    url = f"{SCOS_BASE_URL}/api/v2/courses/participation"
    registration_object: dict = {
        "course_id": course_id,
        "session_id": session_id,
        "user_id": user_id,
        "enroll_date": enroll_date,
    }
    options: set[str] = {"session_start", "session_end"}
    for option in options:
        if option in kwargs:
            registration_object.update(option=kwargs[option])
    LOGGER.info(
        "СЦОС api. Регистрация слушателя на курс: %s",
        registration_object
    )
    try:
        response: requests.Response = requests.post(
            url = url,
            json = [registration_object,],
            headers = HEADERS,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        scos_response = response.json()
        LOGGER.info(
            "СЦОС api. Регистрация слушателя на курс, ответ СЦОС: %s",
            scos_response
        )
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return scos_response

def scos_delete_participation(
    course_id: str,
    session_id: str,
    user_id: str,
) -> Any:
    """
    4.1.1.5. Отмена регистрации слушателя на курсе
    """
    url = f"{SCOS_BASE_URL}/api/v2/courses/participation"
    cancellation_object: dict = {
            "course_id": course_id,
            "session_id": session_id,
            "user_id": user_id,
    }
    LOGGER.info(
        "СЦОС api. Отмена регистрации пользователя на курс: %s",
        cancellation_object
    )
    try:
        response: requests.Response = requests.delete(
            url = url,
            json = [cancellation_object,],
            headers = HEADERS,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        scos_response = response.json()
        LOGGER.info(
            "СЦОС api. Отмена регистрации слушателя на курс, ответ СЦОС: %s",
            scos_response
        )
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return scos_response

def scos_post_subsection_grade(
    course_id: str,
    session_id: str,
    user_id: str,
    date: str,
    rating: float,
    checkpoint_name: str,
    checkpoint_id: str,
) -> Any:
    """
    4.1.2.3. Публикация результатов обучения
    """
    url = f"{SCOS_BASE_URL}/api/v2/courses/results"
    subsection_grade_object: dict = {
            "course_id": course_id,
            "session_id": session_id,
            "user_id": user_id,
            "date": date,
            "rating": rating,
            "checkpoint_name": checkpoint_name,
            "checkpoint_id": checkpoint_id,
    }
    LOGGER.info(
        "СЦОС api. Публикация результатов обучения: %s",
        subsection_grade_object
    )
    try:
        response: requests.Response = requests.post(
            url = url,
            json = [subsection_grade_object,],
            headers = HEADERS,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        scos_response = response.json()
        LOGGER.info(
            "СЦОС api. Публикация результатов обучения, ответ СЦОС: %s",
            scos_response
        )
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return scos_response

def scos_post_course_grade(
    course_id: str,
    session_id: str,
    user_id: str,
    progress: float,
) -> Any:
    """
    4.1.2.6. Публикация прогрессов обучения
    """
    url = f"{SCOS_BASE_URL}/api/v2/courses/results/progress"
    course_grade_object: dict = {
            "course_id": course_id,
            "session_id": session_id,
            "user_id": user_id,
            "progress": progress,
    }
    LOGGER.info(
        "СЦОС api. Публикация прогрессов обучения: %s",
        course_grade_object
    )
    try:
        response: requests.Response = requests.post(
            url = url,
            json = [course_grade_object,],
            headers = HEADERS,
            proxies = PROXIES,
            verify = False,
            timeout = TIMEOUT,
        )
    except requests.exceptions.RequestException as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    try:
        scos_response = response.json()
        LOGGER.info(
            "СЦОС api. Публикация прогрессов обучения, ответ СЦОС: %s",
            scos_response
        )
    except requests.exceptions.JSONDecodeError as exception:
        LOGGER.error("СЦОС api. %s", exception)
        return None
    return scos_response

def get_scos_course(course_key) -> Any:
    """
    Возвращает подробную информацию об одном онлайн курсе со СЦОС если курс
    с соответствующим названием и расположением найден.
    """
    try:
        course_info_from_overview = get_course_info_from_overview(course_key)
        scos_courses = scos_get_courses()
        for course in scos_courses["results"]:
            if course["title"] == course_info_from_overview["title"]:
                course_in_detail = scos_get_course(course["global_id"])
                if (course_in_detail["external_url"] ==
                    course_info_from_overview["external_url"]):
                    return course_in_detail
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС api. %s", exception)
        return None
