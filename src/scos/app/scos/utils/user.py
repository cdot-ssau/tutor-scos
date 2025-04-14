
import logging
from typing import Any

from social_django.models import UserSocialAuth
from django.db.models import Q

from common.djangoapps.student.models.course_enrollment import ( # pylint: disable=import-error
    CourseEnrollment,
 )



LOGGER = logging.getLogger(__name__)



def get_course_enrollments(course_key: str) -> Any:
    try:
        user_in_usersocialauth = Q(
            user_id__in = UserSocialAuth.objects.filter(
                provider = "scos"
            ).values_list("user_id", flat=True)
        )
        enrollments = CourseEnrollment.objects.filter(
            user_in_usersocialauth,
            course_id = course_key
        ).order_by("created")
        return enrollments
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС user. %s", exception)
        return None

def get_user_scos_uid(user_id: int) -> Any:
    try:
        scos_auth = UserSocialAuth.objects.get(
            user_id=user_id,
            provider='scos'
        )
        return scos_auth.uid
    except UserSocialAuth.DoesNotExist:
        return None
    except Exception as exception: # pylint: disable=broad-except
        LOGGER.error("СЦОС user. %s", exception)
        return None
