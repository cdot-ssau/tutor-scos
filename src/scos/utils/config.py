from django.conf import settings
from django.core.exceptions import ImproperlyConfigured

SCOS_BASE_URL = getattr(settings, "SCOS_BASE_URL", "https://online.edu.ru")
SCOS_OIDC_ENDPOINT = getattr(settings, "SCOS_OIDC_ENDPOINT", "https://online.edu.ru")
SCOS_X_CN_UUID = getattr(settings, "SCOS_X_CN_UUID", "")
SCOS_PARTNER_ID = getattr(settings, "SCOS_PARTNER_ID", "")
SCOS_ENABLE_HTTPS = getattr(settings, "SCOS_HTTPS_ENABLE", True)
SCOS_HTTPS_PROXY = getattr(settings, "SCOS_HTTPS_PROXY", "")

LMS_BASE_URL = settings.LMS_BASE
CMS_BASE_URL = settings.CMS_BASE

is_https = str(SCOS_ENABLE_HTTPS).lower() not in ("false", "0", "no", "")
protocol = "https" if is_https else "http"

LMS_URL = f"{protocol}://{LMS_BASE_URL}" if LMS_BASE_URL else ""
CMS_URL = f"{protocol}://{CMS_BASE_URL}" if CMS_BASE_URL else ""
