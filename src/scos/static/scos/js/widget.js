(function () {
    const currentScript = document.currentScript;
    const cmsBaseUrl = currentScript?.dataset?.cmsBaseUrl || new URL(currentScript.src).origin;

    async function checkCourseWidget() {
        if (!window.location.href.includes('course-v1:')) {
            return;
        }

        const getURL = new URL('/scos/course/check/', cmsBaseUrl);
        const courseURL = new URL(window.location.href);
        courseURL.search = '';
        courseURL.hash = '';
        getURL.searchParams.set('course_url', courseURL.toString());

        try {
            const getResponse = await fetch(getURL.toString(), {
                method: 'GET',
                mode: 'cors',
            });

            if (getResponse.redirected) {
                window.location.href = getResponse.url;
                return;
            }

            if (!getResponse.ok) {
                throw new Error(`Response status: ${getResponse.status}`);
            }

            const json = await getResponse.json();
            if (!json?.scos?.widget_url || !json?.scos?.course_id) {
                return;
            }

            const src = new URL('/public/widgets/feedback-widget', json.scos.widget_url);
            src.searchParams.set('courseid', json.scos.course_id);
            src.searchParams.set('version', json.scos.course_version);

            renderWidget(src.toString());
        } catch (error) {
            console.warn('[SCOS Widget] Load error:', error.message);
        }
    }

    function renderWidget(iframeSrc) {
        if (document.getElementById('scos-feedback-section')) {
            return;
        }

        const section = document.createElement('section');
        section.id = 'scos-feedback-section';
        section.classList.add('about', 'container', 'mt-4');

        const header = document.createElement('h2');
        header.textContent = 'Отзывы слушателей';

        const iframe = document.createElement('iframe');
        iframe.setAttribute('src', iframeSrc);
        iframe.setAttribute('scrolling', 'no');
        iframe.setAttribute('width', '100%');
        iframe.setAttribute('height', '350');
        iframe.setAttribute('frameborder', '0');

        section.append(header, iframe);

        const insertIntoDom = () => {
            const target = document.querySelector('main .course-detail-page, main .container, main');
            if (target) {
                target.appendChild(section);
                return true;
            }
            return false;
        };

        if (!insertIntoDom()) {
            const observer = new MutationObserver(() => {
                if (insertIntoDom()) {
                    observer.disconnect();
                }
            });
            observer.observe(document.body, { childList: true, subtree: true });
        }
    }

    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', checkCourseWidget);
    } else {
        checkCourseWidget();
    }
})();