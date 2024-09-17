
import os
import copy
import re
from importlib import import_module
from html.parser import HTMLParser
from typing import Any, Union, Dict, List, Tuple
import json

import requests

from openedx.core.djangoapps.content.course_overviews.models import ( # pylint: disable=import-error
    CourseOverview,
)



SETTINGS = import_module(os.environ["DJANGO_SETTINGS_MODULE"])
LMS_BASE_URL = SETTINGS.LMS_BASE
HTTPS = SETTINGS.HTTPS

if HTTPS == "on":
    LMS_URL = f"https://{LMS_BASE_URL}"
elif HTTPS == "off":
    LMS_URL = f"http://{LMS_BASE_URL}"



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

class AttrValueDescriptor:

    def __set_name__(self, owner, name):
        self._name = name

    def __set__(self, instance, value):
        instance.__dict__[self._name] = value

class CourseInfoDescription(CourseInfoAttr):

    class Description(AttrValueDescriptor):

        def __set__(self, instance, value: list) -> None:
            if value:
                instance.__dict__[self._name] = "<br>".join(value)
            else:
                instance.__dict__[self._name] = None

    value = Description()

class CourseInfoCompetences(CourseInfoAttr):

    class Competences(AttrValueDescriptor):

        def __set__(self, instance, value: list) -> None:
            if value:
                instance.__dict__[self._name] = "\n".join(value)
            else:
                instance.__dict__[self._name] = None

    value = Competences()

class CourseInfoContent(CourseInfoAttr):

    class Content(AttrValueDescriptor):

        def __set__(self, instance, value: list) -> None:
            if value:
                instance.__dict__[self._name] = \
                    f"<ul><li>{'</li><li>'.join(value)}</li></ul>"
            else:
                instance.__dict__[self._name] = None

    value = Content()

class CourseInfoDuration(CourseInfoAttr):

    class Duration(AttrValueDescriptor):

        def __set__(self, instance, value: list):
            if value:
                instance.__dict__[self._name] = {
                    "code": "week",
                    "value": int(value[0])
                }
            else:
                instance.__dict__[self._name] = {
                    "code": "week",
                    "value": None
                }

    value = Duration()

class CourseInfoLectures(CourseInfoAttr):

    class Lectures(AttrValueDescriptor):

        def __set__(self, instance, value: list):
            if value:
                instance.__dict__[self._name] = int(value[0])
            else:
                instance.__dict__[self._name] = None

    value = Lectures()

class CourseInfoLanguage(CourseInfoAttr):

    class Language(AttrValueDescriptor):

        LANGUAGES = {
            "Русский": "ru",
            "ru": "ru",
            "RU": "ru",
            "Ru": "ru",
            "English": "en",
            "en": "en",
            "EN": "en",
            "En": "en",
        }

        def __set__(self, instance, value: list):
            if value:
                if value[0] in self.LANGUAGES:
                    instance.__dict__[self._name] = self.LANGUAGES[value[0]]
                else:
                    instance.__dict__[self._name] = ""
            else:
                instance.__dict__[self._name] = None

    value = Language()

class CourseInfoCert(CourseInfoAttr):

    class Cert(AttrValueDescriptor):

        VALUES = {
            "Есть": "true",
            "Нет": "false",
            "Yes": "true",
            "No": "false",
        }

        def __set__(self, instance, value: list):
            if value:
                if value[0] in self.VALUES:
                    instance.__dict__[self._name] = self.VALUES[value[0]]
                else:
                    instance.__dict__[self._name] = None
            else:
                instance.__dict__[self._name] = None

    value = Cert()

class CourseInfoResults(CourseInfoAttr):

    class Results(AttrValueDescriptor):

        def __set__(self, instance, value: list):
            if value:
                instance.__dict__[self._name] = " ".join(value)
            else:
                instance.__dict__[self._name] = None

    value = Results()

class CourseInfoCredits(CourseInfoAttr):

    class Credits(AttrValueDescriptor):

        def __set__(self, instance, value: list):
            if value:
                instance.__dict__[self._name] = float(value[0])
            else:
                instance.__dict__[self._name] = None

    value = Credits()

class CourseInfoTeachers(CourseInfoAttr):

    class Teachers(AttrValueDescriptor):

        def __set__(self, instance, value: list):
            if value:
                teachers = []
                for teacher in value:
                    teachers.append(
                        {
                            "display_name":[],
                            "image": [],
                            "description": [],
                        }
                    )
                    teachers[-1]["display_name"] = " ".join(teacher["display_name"])
                    teachers[-1]["image"] = LMS_URL + teacher["image"]
                    teachers[-1]["description"] = " ".join(teacher["description"])
                instance.__dict__[self._name] = teachers
            else:
                instance.__dict__[self._name] = None

    value = Teachers()

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
        self.requirements = CourseInfoAttr(
            name = "requirements",
            valuetype = "string[]",
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
        self.direction = CourseInfoAttr(
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
        self.teachers = CourseInfoTeachers(
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

class OverviewHTMLParser(HTMLParser):

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.data: Dict[str, List[str]] = {}
        self.data_read: bool = False
        self.tag_attr: str = ""
        self.tag_count: int = 0
        self.tag: str = ""

    def handle_starttag(
        self,
        tag: str,
        attrs: List[Tuple[str, Union[str, None]]]
    ) -> None:
        if self.data_read is True:
            self.tag_count += 1
        else:
            tag_attrs = [attr[1] for attr in attrs if attr[0] == "data-scos"]
            if tag_attrs:
                self.tag_attr = tag_attrs[0]
                self.data_read = True
                self.tag = tag
        return super().handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        data = data.strip()
        if self.data_read and data:
            if self.tag_attr in self.data:
                self.data[self.tag_attr].append(data)
            else:
                self.data.update({self.tag_attr: [data, ]})

    def handle_endtag(self, tag: str) -> None:
        if self.data_read and self.tag_count == 0 and self.tag == tag:
            self.data_read: bool = False
            self.tag_count: int = 0
            self.tag: str = ""
            self.tag_attr: str = ""
        if self.data_read and self.tag_count > 0:
            self.tag_count -= 1

class TeachersHTMLParser(HTMLParser):

    teacher_attr = [
        "display_name",
        "image",
        "description",
    ]
    void_tags = [
        "img",
        "br",
    ]

    def __init__(self, *args, **kwargs) -> None:
        super().__init__(*args, **kwargs)
        self.teachers: List[Dict[str, Union[List[str], str]]] = []
        self.teacher: bool = False
        self.teacher_tag_count: int = 0
        self.teacher_tag: str = ""
        self.data_read: bool = False
        self.tag_attr: str = ""
        self.tag_count: int = 0
        self.tag: str = ""

    def handle_starttag(
        self,
        tag: str,
        attrs: List[Tuple[str, Union[str, None]]]
    ) -> None:
        if self.data_read is True:
            if tag not in self.void_tags:
                self.tag_count += 1
        else:
            tag_attrs = [
                attr[1] for attr in attrs if attr[0] == "data-scos-teacher"
            ]
            if tag_attrs:
                self.tag_attr = tag_attrs[0]
                if self.tag_attr == "teacher":
                    self.teacher = True
                    self.teachers.append(
                        {
                            "display_name":[],
                            "image": [],
                            "description": [],
                        }
                    )
                    self.tag_attr = ""
                if self.teacher is True and self.tag_attr in self.teacher_attr:
                    self.data_read = True
                    self.tag = tag
                else:
                    self.tag_attr = ""
            if tag == "img" and self.data_read and self.tag_attr == "image":
                img_attrs = [
                    attr[1] for attr in attrs if attr[0] == "src"
                ]
                if  img_attrs:
                    self.teachers[-1][self.tag_attr] = img_attrs[0]
                self.data_read: bool = False
                self.tag_count: int = 0
                self.tag: str = ""
                self.tag_attr: str = ""

        return super().handle_starttag(tag, attrs)

    def handle_data(self, data: str) -> None:
        data = data.strip()
        if self.data_read and data:
            self.teachers[-1][self.tag_attr].append(data)
        return super().handle_data(data)

    def handle_endtag(self, tag: str) -> None:
        if self.data_read and self.tag_count == 0 and self.tag == tag:
            self.data_read: bool = False
            self.tag_count: int = 0
            self.tag: str = ""
            self.tag_attr: str = ""
        if self.data_read and self.tag_count > 0:
            self.tag_count -= 1
        if self.teacher and self.teacher_tag_count and self.teacher_tag == tag:
            self.teacher: bool = False
            self.teacher_tag_count: int = 0
            self.teacher_tag: str = ""
        if self.teacher and self.teacher_tag_count > 0:
            self.teacher_tag_count -= 1
        return super().handle_endtag(tag)



def get_course_key(course_url: str) -> Union[str, None]:
    match = re.match(r"(^.*/courses/)([\w:+-]+)(/.*$|$)", course_url)
    if match:
        return match.group(2)
    return None

def get_course_info_from_about(about_url: str) -> Union[dict, None]:
    try:
        response: requests.Response = requests.get(
            url=about_url,
            timeout = 5.000,
        )
    except requests.exceptions.ConnectTimeout:
        return None
    overview_parser = OverviewHTMLParser()
    teachers_parser = TeachersHTMLParser()
    overview_parser.feed(response.text)
    teachers_parser.feed(response.text)
    course_info_from_about = {
        **overview_parser.data,
        "teachers": teachers_parser.teachers
    }
    return course_info_from_about

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
