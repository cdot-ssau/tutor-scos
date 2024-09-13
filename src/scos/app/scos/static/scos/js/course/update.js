document.addEventListener("DOMContentLoaded", (event) => {
    formatAllJSON();
    expandTextareas();
    courseJSONUpdate();
    addOnChangeEvent();
    addCourseInfoFormEvent(courseAddSendUrl, courseJSON, csrftoken);
});
