
// printing course_json

function formatJSONCode(unformattedJSON) {
    let formattedJSON = JSON.stringify(unformattedJSON, null, "  ");
    formattedJSON = formattedJSON.replaceAll(/\</gi, "&lt");
    formattedJSON = formattedJSON.replaceAll(/\>/gi, "&gt");
    formattedJSON = formattedJSON.replaceAll(/(\"\w*\"):/gi, "<span class=\"keys\">$1</span>:");
    formattedJSON = formattedJSON.replaceAll(/[\{\}\[\]\(\)]/gi, "<span class=\"brackets\">$&</span>");
    return formattedJSON
}

function formatAllJSON() {
    for (let element of document.getElementsByClassName("json-code")) {
        element.innerHTML = formatJSONCode(JSON.parse(element.innerHTML));
    }
}

// expanding textarea

function expandTextareas() {
    const elementsExpandable = document.getElementsByClassName("expandable");
    document.addEventListener("DOMContentLoaded", (event) => {
        for (let element of elementsExpandable) {
            if (element.tagName === "TEXTAREA") {
                element.style.height = element.scrollHeight + "px";
            }
        }
    });
    for (let element of elementsExpandable) {
        if (element.tagName === "TEXTAREA") {
            element.addEventListener("input", (event) => {
                element.style.height = "";
                element.style.height = element.scrollHeight + "px";
            });
        }
    }
}

// add event listener to textarea

function addOnChangeEvent() {
    const elementsValue = document.getElementsByClassName("value");
    const printCourseJSON = document.getElementById("print_course_json");
    for (let element of elementsValue) {
        element.addEventListener("change", (event) => {
            let name = element.getAttribute("name");
            if (element.value) {
                try {
                    courseJSON[name] = JSON.parse(element.value);
                } catch (error) {
                    courseJSON[name] = element.value;
                }
            } else {
                delete courseJSON[element.getAttribute("name")];
            }
            printCourseJSON.innerHTML = formatJSONCode(courseJSON);
        });
    }
}

// update courseJSON on reload

function courseJSONUpdate() {
    const elementsValue = document.getElementsByClassName("value");
    const printCourseJSON = document.getElementById("print_course_json");
    window.addEventListener("load", (event) => {
        for (let element of elementsValue) {
            let name = element.getAttribute("name");
            if (element.value) {
                try {
                    courseJSON[name] = JSON.parse(element.value);
                } catch (error) {
                    courseJSON[name] = element.value;
                }
            }
            printCourseJSON.innerHTML = formatJSONCode(courseJSON);
        }
    });
}

// add event listener to course_info_form

function addCourseInfoFormEvent(url, courseJSON, csrftoken) {
    document.getElementById("course_info_form").addEventListener(
        "submit", async (event) => {
            event.preventDefault();
            sendCourseInfo(url, courseJSON, csrftoken);
        }
    );
}

// processing data

async function sendCourseInfo(url, courseJSON, csrftoken) {
    document.getElementById("send_course_info").disabled = true;
    document.getElementById("print_course_json").innerHTML = formatJSONCode(courseJSON);
    const request = new Request(url, {
        method: "POST",
        body: JSON.stringify(courseJSON),
        headers: {"X-CSRFToken": csrftoken},
        mode: "same-origin"
    });
    try {
        const response = await fetch(request);
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const json = await response.json();
        window.alert(JSON.stringify(json));
    } catch (error) {
            window.alert(error.message);
    } finally {
        document.getElementById("send_course_info").disabled = false;
    }
}

// add event listener to course_info_form

function addCourseIDFormEvent(url) {
    document.getElementById("course_id_form").addEventListener(
        "submit", async (event) => {
            event.preventDefault();
            openCourseByID(url);
        }
    );
}

// open course by ID

async function openCourseByID(url) {
    document.getElementById("course_id_submit").disabled = true;
    let course_id = document.getElementById("course_id_text").value;
    url = url + `?course_id=${course_id}`
    const request = new Request(url, {
        method: "GET",
        mode: 'same-origin'
    });
    try {
        const response = await fetch(request);
        if (response.redirected) {
            window.location.href = response.url;
            return;
        }
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        response.text().then((value) => {
            window.alert(value);
        });
        document.getElementById("course_id_submit").disabled = false;
    } catch (error) {
            window.alert(error.message);
            document.getElementById("course_id_submit").disabled = false;
    }
}

// enable disabled textareas

function enableDisabledTextareas(checked) {
    const disabledTextareas = document.getElementsByClassName("disabled");
    for (let textarea of disabledTextareas) {
        textarea.disabled = !checked;
    }
}

// add event listener to allow-override buttons

function addAllowOverrideEvent() {
    const allowOverrideCheckbox = document.getElementById("allow_override_checkbox");
    allowOverrideCheckbox.addEventListener(
        "change",
        (event) => {
            enableDisabledTextareas(event.target.checked);
        }
    );
}

// reverse status

function reverseStatus(statusString) {
    let newStatusString;
    if (statusString === "ARCHIVED") {
        newStatus = 1;
    } else {
        newStatus = 0;
    }
    return newStatus;
}

// updating status

async function updateCourseStatus(url, csrftoken) {
    const courseStatus = document.getElementById("course_status");
    const courseStatusButton = document.getElementById("course_status_button");
    const putURL = new URL(url);
    const getURL = new URL(url);
    putURL.searchParams.set("is_active", reverseStatus(courseStatus.innerText));
    const putRequest = new Request(putURL, {
        method: "PUT",
        headers: {"X-CSRFToken": csrftoken},
        mode: "same-origin"
    });
    const getRequest = new Request(getURL, {
        method: "GET",
        mode: "same-origin"
    });
    courseStatusButton.disabled = true;
    try {
        const putResponse = await fetch(putRequest);
        if (putResponse.redirected) {
            window.location.href = putResponse.url;
            return;
        }
        if (!putResponse.ok) {
            throw new Error(`Response status: ${putResponse.status}`);
        }
        const json = await putResponse.json();
        window.alert(JSON.stringify(json));
    } catch (error) {
        window.alert(error.message);
    } finally {
        courseStatusButton.disabled = false;
    }
    try {
        const getResponse = await fetch(getRequest);
        if (getResponse.redirected) {
            window.location.href = getResponse.url;
            return;
        }
        if (!getResponse.ok) {
            throw new Error(`Response status: ${getResponse.status}`);
        }
        courseStatus.innerText = await getResponse.text();
    } catch (error) {
            window.alert(error.message);
    }
}

// add event listener to course_status_button

function addCourseStatusButtonEvent(url, csrftoken) {
    document.getElementById("course_status_form").addEventListener(
        "submit", async (event) => {
            event.preventDefault();
            updateCourseStatus(url, csrftoken);
        }
    );
}