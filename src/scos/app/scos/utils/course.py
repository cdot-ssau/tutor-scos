
import copy
import re
from typing import Any, Union, Dict, List
import json

import requests

from bs4 import BeautifulSoup
from bs4.element import Tag

from openedx.core.djangoapps.content.course_overviews.models import ( # pylint: disable=import-error
    CourseOverview,
)

from .config import (
    LMS_URL,
)



class AttrValueDescriptor:

    def __set_name__(self, owner, name) -> None:
        self._name = name

    def __set__(self, instance, value: Union[List[Tag], Any]) -> None:
        if self.tag_in_value(value):
            value = value[0].get_text()
        instance.__dict__[self._name] = value

    @staticmethod
    def tag_in_value(value: list) -> bool:
        return (
            isinstance(value, list) and
            not all(not isinstance(e, Tag) for e in value)
        )


class CourseInfoAttr:

    def __init__(
        self,
        name: str,
        valuetype: str,
        description: str,
        required: bool,
        moderated: bool,
        value: Any = None
    ) -> None:
        self.name = name
        self.valuetype = valuetype
        self.description = description
        self.required = required
        self.moderated = moderated
        self.value = value

    value = AttrValueDescriptor()

class CourseInfoDescription(CourseInfoAttr):

    class Description(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], str]) -> None:
            if self.tag_in_value(value):
                description = []
                for v in value:
                    if isinstance(v, Tag):
                        description += (
                            str(c) for c in v.contents if c.text.strip()
                        )
                value = "".join(description)
            instance.__dict__[self._name] = value

    value = Description()

class CourseInfoCompetences(CourseInfoAttr):

    class Competences(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], str]) -> None:
            if self.tag_in_value(value):
                competences = []
                for v in value:
                    if isinstance(v, Tag):
                        competences += (
                            str(c) for c in v.contents if c.text.strip()
                        )
                value = "".join(competences)
            instance.__dict__[self._name] = value

    value = Competences()

class CourseInfoRequirements(CourseInfoAttr):

    class Requirements(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], List[str]]) -> None:
            if self.tag_in_value(value):
                requirements = []
                for v in value:
                    if isinstance(v, Tag):
                        requirements += (
                            c.get_text() for c in v.contents if c.text.strip()
                        )
                value = requirements
            instance.__dict__[self._name] = value

    value = Requirements()

class CourseInfoContent(CourseInfoAttr):

    class Content(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], str]) -> None:
            if self.tag_in_value(value):
                content = []
                for v in value:
                    if isinstance(v, Tag):
                        content += (
                            str(c) for c in v.contents if c.text.strip()
                        )
                value = "".join(content)
            instance.__dict__[self._name] = value

    value = Content()

class CourseInfoDirection(CourseInfoAttr):

    class Direction(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], List[str]]) -> None:
            if self.tag_in_value(value):
                direction = []
                for v in value:
                    if isinstance(v, Tag):
                        direction += (
                            c.get_text() for c in v.contents if c.text.strip()
                        )
                value = direction
            instance.__dict__[self._name] = value

    value = Direction()

class CourseInfoDuration(CourseInfoAttr):

    class Duration(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], int, dict]) -> None:
            if self.tag_in_value(value):
                try:
                    value = int(value[0].get_text())
                except ValueError:
                    value = 1
            if isinstance(value, int):
                value = {
                    "code": "week",
                    "value": value
                }
            instance.__dict__[self._name] = value

    value = Duration()

class CourseInfoLectures(CourseInfoAttr):

    class Lectures(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], int]) -> None:
            if self.tag_in_value(value):
                try:
                    value = int(value[0].get_text())
                except ValueError:
                    return None
            instance.__dict__[self._name] = value

    value = Lectures()

class CourseInfoLanguage(CourseInfoAttr):

    class Language(AttrValueDescriptor):

        LANGUAGES = {
            "Русский": "ru",
            "русский": "ru",
            "ru": "ru",
            "RU": "ru",
            "Ru": "ru",
            "English": "en",
            "english": "en",
            "en": "en",
            "EN": "en",
            "En": "en",
        }

        def __set__(self, instance, value: Union[List[Tag], str]) -> None:
            if self.tag_in_value(value):
                value = value[0].get_text()
            if value in self.LANGUAGES:
                value = self.LANGUAGES[value]
            instance.__dict__[self._name] = value

    value = Language()

class CourseInfoCert(CourseInfoAttr):

    class Cert(AttrValueDescriptor):

        VALUES = {
            "Есть": "true",
            "есть": "true",
            "Yes": "true",
            "yes": "true",
            "Нет": "false",
            "нет": "false",
            "No": "false",
            "no": "false",
        }

        def __set__(self, instance, value: Union[List[Tag], str]) -> None:
            if self.tag_in_value(value):
                value = value[0].get_text()
            if value in self.VALUES:
                value = self.VALUES[value]
            instance.__dict__[self._name] = value

    value = Cert()

class CourseInfoResults(CourseInfoAttr):

    class Results(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], str]) -> None:
            if self.tag_in_value(value):
                results = []
                for v in value:
                    if isinstance(v, Tag):
                        results += (
                            str(c) for c in v.contents if c.text.strip()
                        )
                value = "".join(results)
            instance.__dict__[self._name] = value

    value = Results()

class CourseInfoCredits(CourseInfoAttr):

    class Credits(AttrValueDescriptor):

        def __set__(self, instance, value: Union[List[Tag], float]) -> None:
            if self.tag_in_value(value):
                try:
                    value = float(value[0].get_text())
                except ValueError:
                    return None
            instance.__dict__[self._name] = value

    value = Credits()

class CourseInfo:

    def __init__(self) -> None:
        self.title = CourseInfoAttr(
            name = "title",
            valuetype = "string",
            description = "Название онлайн-курса",
            required = True,
            moderated = True
        )
        self.started_at = CourseInfoAttr(
            name = "started_at",
            valuetype = "string",
            description = "Дата ближайшего запуска",
            required = True,
            moderated = False
        )
        self.finished_at = CourseInfoAttr(
            name = "finished_at",
            valuetype = "string",
            description = "Дата окончания онлайн-курса",
            required = False,
            moderated = False
        )
        self.enrollment_finished_at = CourseInfoAttr(
            name = "enrollment_finished_at",
            valuetype = "string",
            description = "Дата окончания записи на онлайн-курс",
            required = False,
            moderated = False
        )
        self.image = CourseInfoAttr(
            name = "image",
            valuetype = "string",
            description = "Ссылка на изображение",
            required = True,
            moderated = False
        )
        self.description = CourseInfoDescription(
            name = "description",
            valuetype = "string",
            description = "Описание онлайн-курса",
            required = True,
            moderated = True
        )
        self.competences = CourseInfoCompetences(
            name = "competences",
            valuetype = "string",
            description = "Строка с набором компетенций. Для разделения " \
                "строк по позициям необходимо использовать \"\\n\"",
            required = True,
            moderated = True
        )
        self.requirements = CourseInfoRequirements(
            name = "requirements",
            valuetype = "list",
            description = "Массив строк - входных требований к обучающемуся",
            required = True,
            moderated = True
        )
        self.content = CourseInfoContent(
            name = "content",
            valuetype = "string",
            description = "Содержание онлайн-курса",
            required = True,
            moderated = True
        )
        self.external_url = CourseInfoAttr(
            name = "external_url",
            valuetype = "string",
            description = "Ссылка на онлайн-курс на сайте Платформы",
            required = True,
            moderated = False
        )
        self.direction = CourseInfoDirection(
            name = "direction",
            valuetype = "list",
            description = "Массив идентификаторов направлений",
            required = True,
            moderated = False
        )
        self.institution = CourseInfoAttr(
            name = "institution",
            valuetype = "string",
            description = "Идентификатор Правообладателя",
            required = True,
            moderated = False
        )
        self.duration = CourseInfoDuration(
            name = "duration",
            valuetype = "CourseDuration",
            description = "Длительность онлайн-курса в неделях",
            required = True,
            moderated = True
        )
        self.lectures = CourseInfoLectures(
            name = "lectures",
            valuetype = "integer",
            description = "Количество лекций",
            required = True,
            moderated = True
        )
        self.language = CourseInfoLanguage(
            name = "language",
            valuetype = "string",
            description = "Язык онлайн-курса",
            required = False,
            moderated = False
        )
        self.cert = CourseInfoCert(
            name = "cert",
            valuetype = "string",
            description = "Возможность получить сертификат",
            required = True,
            moderated = False
        )
        self.visitors = CourseInfoAttr(
            name = "visitors",
            valuetype = "integer",
            description = "Количество записей на сессию онлайн-курса",
            required = False,
            moderated = False
        )
        self.teachers = CourseInfoAttr(
            name = "teachers",
            valuetype = "list",
            description = "Массив лекторов",
            required = True,
            moderated = True
        )
        self.transfers = CourseInfoAttr(
            name = "transfers",
            valuetype = "list",
            description = "Массив перезачётов",
            required = False,
            moderated = False
        )
        self.results = CourseInfoResults(
            name = "results",
            valuetype = "string",
            description = "Результаты обучения",
            required = True,
            moderated = True
        )
        self.accreditated = CourseInfoAttr(
            name = "accreditated",
            valuetype = "string",
            description = "Аккредитация",
            required = False,
            moderated = False
        )
        self.hours = CourseInfoAttr(
            name = "hours",
            valuetype = "integer",
            description = "Объем онлайн-курса, в часах",
            required = False,
            moderated = False
        )
        self.hours_per_week = CourseInfoAttr(
            name = "hours_per_week",
            valuetype = "integer",
            description = "Требуемое время для изучения онлайн-курса, часов в неделю",
            required = False,
            moderated = False
        )
        self.business_version = CourseInfoAttr(
            name = "business_version",
            valuetype = "string",
            description = "Версия курса",
            required = True,
            moderated = False
        )
        self.promo_url = CourseInfoAttr(
            name = "promo_url",
            valuetype = "string",
            description = "Ссылка на проморолик",
            required = False,
            moderated = False
        )
        self.promo_lang = CourseInfoAttr(
            name = "promo_lang",
            valuetype = "string",
            description = "Язык проморолика",
            required = False,
            moderated = False
        )
        self.subtitles_lang = CourseInfoAttr(
            name = "subtitles_lang",
            valuetype = "string",
            description = "Язык субтитров",
            required = False,
            moderated = False
        )
        self.estimation_tools = CourseInfoAttr(
            name = "estimation_tools",
            valuetype = "string",
            description = "Оценочные средства",
            required = False,
            moderated = False
        )
        self.proctoring_service = CourseInfoAttr(
            name = "proctoring_service",
            valuetype = "string",
            description = "Используемый сервис прокторинга (либо перечень " \
                "сервисов через \",\")",
            required = False,
            moderated = False
        )
        self.sessionid = CourseInfoAttr(
            name = "sessionid",
            valuetype = "string",
            description = "Идентификатор сессии курса на платформе",
            required = False,
            moderated = False
        )
        self.credits = CourseInfoCredits(
            name = "credits",
            valuetype = "number",
            description = "Трудоёмкость курса в з.е.",
            required = True,
            moderated = False
        )
        self.proctoring_type = CourseInfoAttr(
            name = "proctoring_type",
            valuetype = "string",
            description = "Тип(-ы) используемого(-ых) сервиса(-ов) " \
                "прокторинга (либо перечень через \",\")",
            required = False,
            moderated = False
        )
        self.assessment_description = CourseInfoAttr(
            name = "assessment_description",
            valuetype = "string",
            description = "Текстовое описание системы оценивания (критерии " \
                "и шкалы оценивания)",
            required = False,
            moderated = False
        )

    @staticmethod
    def expand_vars(obj) -> dict:
        if hasattr(obj, "__dict__"):
            attrs: dict = copy.deepcopy(vars(obj))
            for attr in attrs:
                attrs[attr] = CourseInfo.expand_vars(attrs[attr])
            return attrs
        return obj

    def dictionary(self) -> dict:
        return CourseInfo.expand_vars(self)

    def json(self) -> str:
        course_info: dict = {
            getattr(self, attr).name: getattr(self, attr).value
            for attr in vars(self)
            if getattr(self, attr).value
        }
        return json.dumps(
            CourseInfo.expand_vars(course_info),
            ensure_ascii=False
        )

def get_course_info_from_about(about_url: str) -> Union[dict, None]:
    def data_scos(tag):
        return tag.has_attr("data-scos")
    data: Dict[str, Tag] = {}
    teachers: List[Dict[str, Union[List[str], str]]] = []
    try:
        response: requests.Response = requests.get(
            url=about_url,
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    except requests.exceptions.ReadTimeout:
        return None
    about = BeautifulSoup(response.text, "html.parser")
    for tag in about.find_all(data_scos):
        if tag["data-scos"] in data:
            data[tag["data-scos"]].append(tag)
        else:
            data.update({tag["data-scos"]: [tag, ]})
    for tag in about.find_all(attrs={"data-scos-teacher": "teacher"}):
        teachers.append({})
        teachers[-1]["display_name"] = " ".join(
            tag.find(
                attrs={"data-scos-teacher": "display_name"}
            ).stripped_strings
        )
        teachers[-1]["image"] = LMS_URL + tag.find(
            attrs={"data-scos-teacher": "image"}
        )["src"]
        teachers[-1]["description"] =  " ".join(
            tag.find(
                attrs={"data-scos-teacher": "description"}
            ).stripped_strings
        )
    if teachers:
        data.update({"teachers": teachers})
    return data

def get_course_key(course_url: str) -> Union[str, None]:
    match = re.match(r"(^.*/courses/)([\w:+-]+)(/.*$|$)", course_url)
    if match:
        return match.group(2)
    return None

def get_course_info_from_overview(course_key: str) -> Union[dict, None]:
    course_overview = CourseOverview.get_from_id(course_key)
    if course_overview is None:
        return None
    def process_date(value):
        if value is None:
            return None
        return value.date().isoformat()
    course_info_from_overview = {
        "sessionid": str(course_overview.id),
        "title": course_overview.display_name,
        "started_at": process_date(course_overview.start),
        "finished_at": process_date(course_overview.end),
        "enrollment_finished_at": process_date(course_overview.enrollment_end),
        "image": LMS_URL + course_overview.course_image_url,
        "external_url": f"{LMS_URL}/courses/{str(course_overview.id)}/about",
        "hours_per_week": course_overview.effort,
        "promo_url": course_overview.course_video_url
    }
    return course_info_from_overview

def get_course_info(course_key: str) -> Union[CourseInfo, None]:
    course_info_from_overview = get_course_info_from_overview(course_key)
    course_info_from_about = get_course_info_from_about(
        f"{LMS_URL}/courses/{course_key}/about"
    )
    if course_info_from_about is None:
        return None
    course_info_from = {
        **course_info_from_overview,
        **course_info_from_about,
    }
    course_info = CourseInfo()
    for attr, value in course_info_from.items():
        if hasattr(course_info, attr):
            setattr(getattr(course_info, attr), "value", value)
    return course_info
