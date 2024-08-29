


PATCHES = [
    {
        "file": "/openedx/edx-platform/cms/urls.py",
        "add_to_the_end": \
"""
# SCOS Dashboard
urlpatterns.append(path('scos/', include('cms.djangoapps.scos.urls', namespace='scos')))
""",
    },
    {
        "file": "/openedx/edx-platform/cms/envs/common.py",
        "add_to_the_end": \
"""
# SCOS App
INSTALLED_APPS.append('cms.djangoapps.scos')
""",
    },
    {
        "file": "/openedx/edx-platform/lms/templates/courseware/course_about.html",
        "search_text": "${clean_dangerous_html(get_course_about_section(request, course, \"overview\"))}",
        "replace_text": "${clean_dangerous_html(get_course_about_section(request, course, \"overview\"))}" + \
"""
        % if scos:
          <section class="about">
            <h2>Отзывы слушателей</h2>
            <iframe src="${scos['base_url']}/public/widgets/feedback-widget?courseid=${scos['course_id']}&version=${scos['course_version']}" scrolling="no" width="95%" height="350" frameborder="0"></iframe>
          </section>
        % endif
""",
    },
    {
        "file": "/openedx/edx-platform/lms/djangoapps/courseware/views/views.py",
        "search_text": "course_about_template = 'courseware/course_about.html'",
        "replace_text": "course_about_template = 'courseware/course_about.html'" + \
"""
        from cms.djangoapps.scos.utils.scos_api import SCOS_BASE_URL, get_scos_course
        scos_course = get_scos_course(course_key)
        if scos_course:
            context.update(
                {
                    "scos": {
                        "base_url": SCOS_BASE_URL,
                        "course_id": scos_course["global_id"],
                        "course_version": scos_course["business_version"],
                    }
                }
            )
"""
    }
]



def apply_patch(
    file: str,
    search_text: str = "",
    replace_text: str = "",
    add_to_the_end: str = ""
) -> None:

    with open(file, "r", encoding="utf-8") as f:
        data = f.read()
        if search_text:
            data = data.replace(search_text, replace_text)
        data += add_to_the_end

    with open(file, "w", encoding="utf-8") as f:
        f.write(data)



if __name__ == "__main__":
    for patch in PATCHES:
        apply_patch(**patch)
