"""
СЦОС OpenId backend
"""

from requests import request

from urllib3 import disable_warnings
from urllib3.exceptions import InsecureRequestWarning

from social_core.backends.open_id_connect import OpenIdConnectAuth
from social_core.utils import (SSLHttpAdapter, user_agent)
from social_core.exceptions import AuthFailed

from .config import (
    SCOS_OIDC_ENDPOINT,
    SCOS_HTTPS_PROXY,
)

disable_warnings(InsecureRequestWarning)

PROXIES = {}

if SCOS_HTTPS_PROXY:
    PROXIES.update({"https":SCOS_HTTPS_PROXY})



class SCOSAuthBackend(OpenIdConnectAuth):
    """
    OpenID Connect backend для идентификации и аутентификации СЦОС
    """
    name = "scos"
    OIDC_ENDPOINT = SCOS_OIDC_ENDPOINT
    EXTRA_DATA = [
        ("expires_in", "expires_in", True),
        ("refresh_token", "refresh_token", True),
        ("id_token", "id_token", True),
        ("other_tokens", "other_tokens", True),
    ]
    DEFAULT_SCOPE = ["openid", "email"]
    JWT_DECODE_OPTIONS = {"verify_at_hash": False}

    def get_user_details(self, response):
        """
        Возвращает информацию о пользователе СЦОС
        """
        username_key = self.setting("USERNAME_KEY", default=self.USERNAME_KEY)
        name = response.get("name") or ""
        fullname, first_name, last_name = self.get_user_names(name)
        return {
            "username": response.get(username_key),
            "email": response.get("email"),
            "fullname": fullname,
            "first_name": first_name,
            "last_name": last_name,
        }

# redefining BaseAuth.request

    def request(self, url, method="GET", *args, **kwargs):
        kwargs.setdefault("headers", {})
        if self.setting("PROXIES") is not None:
            kwargs.setdefault("proxies", self.setting("PROXIES"))

        if self.setting("VERIFY_SSL") is not None:
            kwargs.setdefault("verify", self.setting("VERIFY_SSL"))
        kwargs.setdefault(
            "timeout",
            self.setting("REQUESTS_TIMEOUT") or self.setting("URLOPEN_TIMEOUT"),
        )
        if self.SEND_USER_AGENT and "User-Agent" not in kwargs["headers"]:
            kwargs["headers"]["User-Agent"] = self.setting("USER_AGENT") or user_agent()

        try:
            if self.SSL_PROTOCOL:
                session = SSLHttpAdapter.ssl_adapter_session(self.SSL_PROTOCOL)
                response = session.request(method, url, *args, **kwargs)
            else:
                response = request(method, url, *args, proxies = PROXIES, verify = False, **kwargs)
        except ConnectionError as err:
            raise AuthFailed(self, str(err))
        response.raise_for_status()
        return response
