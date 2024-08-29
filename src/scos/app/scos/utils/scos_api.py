"""
SCOS API utils.

Документация по API СЦОС:
https://tech.online.edu.ru/files/api.pdf - Описание программных интерфейсов
государственной информационной системы "Современная цифровая образовательная
среда", размещенной в информационно-телекоммуникационной сети "Интернет" по
адресу online.edu.ru
"""

import os
import codecs
import logging
from typing import Any, List
import yaml

import requests

from .course import (
    get_course_info_from_overview,
)


LOGGER = logging.getLogger(__name__)

CONFIG_FILE = os.environ["CMS_CFG"]
with codecs.open(CONFIG_FILE, encoding="utf-8") as f:
    __config__ = yaml.safe_load(f)
    SCOS_BASE_URL = __config__["SCOS_BASE_URL"]
    SCOS_X_CN_UUID = __config__["SCOS_X_CN_UUID"]
    SCOS_PARTNER_ID = __config__["SCOS_PARTNER_ID"]
HEADERS_GET = {
    "X-CN-UUID": SCOS_X_CN_UUID,
    "Accept": "application/json",
}
HEADERS = {
    "X-CN-UUID": SCOS_X_CN_UUID,
    "Content-type": "application/json",
    "Accept": "application/json",
}



def scos_connection_check() -> str:
    """
    1. Проверка подключения к API тестового контура ГИС СЦОС
    https://tech.online.edu.ru/files/3_apllication_instructions.pdf
    """
    try:
        response: requests.Response = requests.get(
            url = f"{SCOS_BASE_URL}/api/v2/connections/check",
            headers = HEADERS_GET,
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return "Connection timeout"
    return str(response.status_code)

def scos_get_platforms() -> Any:
    """
    3.1.10. Список всех платформ
    """
    try:
        response: requests.Response = requests.get(
            url = f"{SCOS_BASE_URL}/api/v2/registry/partners/platforms",
            headers = HEADERS_GET,
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        platforms = response.json()
    except requests.exceptions.JSONDecodeError:
        return None
    return platforms

def scos_get_rightholders() -> Any:
    """
    3.1.11. Список всех Правообладателей
    """
    try:
        response: requests.Response = requests.get(
            url = f"{SCOS_BASE_URL}/api/v2/registry/partners/rightholders",
            headers = HEADERS_GET,
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        rightholders = response.json()
    except requests.exceptions.JSONDecodeError:
        return None
    return rightholders

def scos_partners_dict(partners: dict) -> dict:
    """
    Возвращает словарь из списка, ключ - global_id
    """
    partners = {row["global_id"]: row for row in partners["rows"]}
    return partners

def scos_get_courses(**kwargs) -> Any:
    """
    3.1.14. Список онлайн-курсов
    
    Возвращает список онлайн-курсов. Дополнительно можно задать параметры
фильтра для следующих атрибутов: language, institution_id, partner_id,
direction_id, activity_id. По умолчанию используется фильтр по идентификатору
платформы - partner_id.
    """
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
            url = f"{SCOS_BASE_URL}/api/v2/registry/courses",
            headers = HEADERS_GET,
            params = params,
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        scos_courses = response.json()
    except requests.exceptions.JSONDecodeError:
        return None
    return scos_courses

def scos_get_course(global_id: str) -> Any:
    """
    3.1.15. Получение одного онлайн-курса
    """
    try:
        response: requests.Response = requests.get(
            url = f"{SCOS_BASE_URL}/api/v2/registry/courses/{global_id}",
            headers = HEADERS_GET,
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        course_info = response.json()
    except requests.exceptions.JSONDecodeError:
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
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        scos_response = response.json()
    except requests.exceptions.JSONDecodeError:
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
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        scos_response = response.json()
    except requests.exceptions.JSONDecodeError:
        return None
    return scos_response

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
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        scos_response = response.json()
        LOGGER.info(
            "СЦОС api. Регистрация слушателя на курс, ответ СЦОС: %s",
            scos_response
        )
    except requests.exceptions.JSONDecodeError:
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
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        scos_response = response.json()
        LOGGER.info(
            "СЦОС api. Отмена регистрации слушателя на курс, ответ СЦОС: %s",
            scos_response
        )
    except requests.exceptions.JSONDecodeError:
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
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        scos_response = response.json()
        LOGGER.info(
            "СЦОС api. Публикация результатов обучения, ответ СЦОС: %s",
            scos_response
        )
    except requests.exceptions.JSONDecodeError:
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
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    try:
        scos_response = response.json()
        LOGGER.info(
            "СЦОС api. Публикация прогрессов обучения, ответ СЦОС: %s",
            scos_response
        )
    except requests.exceptions.JSONDecodeError:
        return None
    return scos_response

def get_scos_course(course_key) -> Any:
    """
    Возвращает подробную информацию об одном онлайн курсе со СЦОС если курс
с соответствующим названием и расположением найден.
    """
    course_info_from_overview = get_course_info_from_overview(course_key)
    if course_info_from_overview is None:
        return None
    scos_courses = scos_get_courses()
    if scos_courses is None:
        return None
    for course in scos_courses["results"]:
        if course["title"] == course_info_from_overview["title"]:
            course_in_detail = scos_get_course(course["global_id"])
            if (course_in_detail["external_url"] ==
                course_info_from_overview["external_url"]):
                return course_in_detail
    return None
