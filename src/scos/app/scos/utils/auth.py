"""
СЦОС OpenId backend
"""

import os
import codecs
import yaml

from social_core.backends.open_id_connect import OpenIdConnectAuth



CONFIG_FILE = os.environ["LMS_CFG"]

with codecs.open(CONFIG_FILE, encoding="utf-8") as f:
    __config__ = yaml.safe_load(f)
    SCOS_OIDC_ENDPOINT = __config__["SCOS_OIDC_ENDPOINT"]



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
