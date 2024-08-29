import logging
from typing import Any

from celery import shared_task

from opaque_keys.edx.keys import UsageKey

from lms.djangoapps.course_api.blocks.api import get_blocks # pylint: disable=import-error

from .scos_api import (
    scos_post_participation,
    scos_delete_participation,
    scos_post_subsection_grade,
    scos_post_course_grade,
    get_scos_course,
)

from .user import (
    get_user_scos_uid,
)



LOGGER = logging.getLogger(__name__)



@shared_task
def user_enrolled(event: dict) -> None:
    user_id: int = int(event["data"]["user_id"])
    course_key: str = event["data"]["course_id"]
    user_scos_uid: str = get_user_scos_uid(user_id)
    if user_scos_uid is not None:
        scos_course = get_scos_course(course_key)
        if scos_course is not None:
            timestamp = event["timestamp"].replace(microsecond=0).isoformat()
            scos_post_participation(
                course_id = scos_course["global_id"],
                session_id = course_key,
                user_id = user_scos_uid,
                enroll_date = timestamp,
            )

@shared_task
def user_unenrolled(event: dict) -> None:
    user_id: int = int(event["data"]["user_id"])
    course_key: str = event["data"]["course_id"]
    user_scos_uid: str = get_user_scos_uid(user_id)
    if user_scos_uid is not None:
        scos_course = get_scos_course(course_key)
        if scos_course is not None:
            scos_delete_participation(
                course_id = scos_course["global_id"],
                session_id = course_key,
                user_id = user_scos_uid,
            )

@shared_task
def subsection_grade(event: dict) -> None:
    user_id: int = int(event["data"]["user_id"])
    course_key: str = event["data"]["course_id"]
    user_scos_uid: str = get_user_scos_uid(user_id)
    if user_scos_uid is not None:
        scos_course = get_scos_course(course_key)
        if scos_course is not None:
            timestamp = event["timestamp"].replace(microsecond=0).isoformat()
            rating: float = round(
                (event["data"]["weighted_graded_earned"]
                / event["data"]["weighted_graded_possible"]) * 100.0,
                2
            )
            block_id: str = event["data"]["block_id"]
            subsection_display_name: str = get_blocks(
                None,
                UsageKey.from_string(block_id),
                requested_fields = ["display_name", ]
            )["blocks"][block_id]["display_name"]
            scos_post_subsection_grade(
                course_id = scos_course["global_id"],
                session_id = course_key,
                user_id = user_scos_uid,
                date = timestamp,
                rating = rating,
                checkpoint_name = subsection_display_name,
                checkpoint_id = block_id,
            )

@shared_task
def course_grade(event: dict) -> None:
    user_id: int = int(event["data"]["user_id"])
    course_key: str = event["data"]["course_id"]
    user_scos_uid: str = get_user_scos_uid(user_id)
    if user_scos_uid is not None:
        scos_course = get_scos_course(course_key)
        if scos_course is not None:
            progress: float = round(event["data"]["percent_grade"]*100.0, 2)
            scos_post_course_grade(
                course_id = scos_course["global_id"],
                session_id = course_key,
                user_id = user_scos_uid,
                progress = progress,
            )
