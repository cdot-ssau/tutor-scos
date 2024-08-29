"""
СЦОС Event tracker
"""

import logging

from common.djangoapps.track.backends import BaseBackend # pylint: disable=import-error

from .tasks import (
    user_enrolled,
    user_unenrolled,
    subsection_grade,
    course_grade,
)



LOGGER = logging.getLogger(__name__)



class SCOSEventTrackingBackend(BaseBackend):

    def send(self, event):

        if event["name"] == "edx.course.enrollment.activated":
            self.send_to_celery(user_enrolled, event)

        if event["name"] == "edx.course.enrollment.deactivated":
            self.send_to_celery(user_unenrolled, event)

        if event["name"] == "edx.grades.subsection.grade_calculated":
            self.send_to_celery(subsection_grade, event)

        if event["name"] == "edx.grades.course.grade_calculated":
            self.send_to_celery(course_grade, event)

    def send_to_celery(
        self,
        task: callable,
        *args,
        **kwargs) -> None:
        try:
            task.apply_async(
                args = args,
                kwargs = kwargs,
            )
        except Exception as exception:  # pylint: disable=broad-except
            logging.error(
                "Не получилось добавить задачу СЦОС в очередь: %s",
                exception,
            )
