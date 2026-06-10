


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
        "search_text": "(get_course_about_section(request, course, \"overview\"))}",
        "replace_text": "(get_course_about_section(request, course, \"overview\"))}" + \
"""
        <%!
          from cms.djangoapps.scos.utils.config import CMS_URL
        %>
        <script id="scos_widget">
          async function checkCourseWidget() {
            const getURL = new URL("${CMS_URL}/scos/course/check/");
            const courseURL = new URL(window.location.href);
            getURL.searchParams.set("course_url", courseURL);
            const getRequest = new Request(getURL, {
              method: "GET",
              mode: "cors",
            });
            try {
              const getResponse = await fetch(getRequest);
              if (getResponse.redirected) {
                window.location.href = getResponse.url;
                return;
              }
              <%text>
              if (!getResponse.ok) {
                throw new Error(`Response status: ${getResponse.status}`);
              }
              const json = await getResponse.json();
              const section = document.createElement("section");
              const header = document.createElement("h2");
              const iframe = document.createElement("iframe");
              const src = new URL(`${json["scos"]["widget_url"]}/public/widgets/feedback-widget`)
              src.searchParams.set("courseid", json["scos"]["course_id"]);
              src.searchParams.set("version", json["scos"]["course_version"]);
              section.classList.add("about");
              section.append(header);
              section.append(iframe);
              header.textContent = "Отзывы слушателей";
              iframe.setAttribute("src", src.toString());
              iframe.setAttribute("scrolling", "no");
              iframe.setAttribute("width", "95%");
              iframe.setAttribute("height", "350");
              iframe.setAttribute("frameborder", "0");
              document.getElementById("scos_widget").after(section);
              </%text>
            } catch (error) {
              console.log(error.message);
            }
          }
          checkCourseWidget();
        </script>
""",
    },
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
