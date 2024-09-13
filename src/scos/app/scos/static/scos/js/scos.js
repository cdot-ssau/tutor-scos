
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
            if (element.value) {
                courseJSON[element.getAttribute("name")] = element.value;
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
            if (element.value) {
                courseJSON[element.getAttribute("name")] = element.value;
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
        headers: {'X-CSRFToken': csrftoken},
        mode: 'same-origin'
    });
    try {
        const response = await fetch(request);
        if (!response.ok) {
            throw new Error(`Response status: ${response.status}`);
        }
        const json = await response.json();
        window.alert(JSON.stringify(json));
        if (response.redirected) {
            window.location.href = response.url;
        }
        document.getElementById("send_course_info").disabled = false;
    } catch (error) {
            window.alert(error.message);
            document.getElementById("send_course_info").disabled = false;
    }
}
