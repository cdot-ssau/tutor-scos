class SCOSCatalogLoader {
    cmsBaseUrl = '';

    constructor({ config }) {
        this.cmsBaseUrl = config.STUDIO_BASE_URL;
    }

    loadScript() {
        if (!this.cmsBaseUrl) {
            console.warn('[SCOSCatalogLoader] Delaying asset loading: STUDIO_BASE_URL is unassigned.');
            return;
        }
        const src = new URL('/static/scos/js/widget.js', this.cmsBaseUrl).href;
        if (!document.querySelector(`script[src="${src}"]`)) {
            const script = document.createElement('script');
            script.src = src;
            script.defer = true;
            script.dataset.cmsBaseUrl = this.cmsBaseUrl;
            document.head.appendChild(script);
        }
    }
}