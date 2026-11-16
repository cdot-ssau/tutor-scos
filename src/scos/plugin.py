from __future__ import annotations

import os
import os.path
import textwrap
from importlib.resources import files
from typing import Union
import appdirs
from tutor import hooks, fmt
from tutor import config as tutor_config
from tutor.types import Config
from tutor.__about__ import __app__
from tutormfe.hooks import EXTERNAL_SCRIPTS
from .__about__ import __version__



ROOT_PATH: str = (os.path.expanduser(os.environ.get("TUTOR_ROOT", ""))
    or appdirs.user_data_dir(__app__)
)

hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("SCOS_VERSION", __version__),
    ]
)

RESOURCES = files("scos")

SCOS_LOADERS = (
    (RESOURCES / "scos_loaders.js")
    .read_text(encoding="utf-8")
)



def scos_config(key: str, default: str = "", echo: bool = False) -> str:
    """
    Устанавливаем настройки по умолчанию и выводим сообщение о необходимости
    обновить настройки по умолчанию
    """
    config: Config = tutor_config.load_minimal(ROOT_PATH)
    value: Union[str, None] = config.get(key)
    if value is None:
        value = default
        config.update({key: value})
        tutor_config.save_config_file(ROOT_PATH, config)
    if value == default and echo:
        fmt.echo_info(
            f"Обновите переменную {key} в конфигурационном файле:\n"
            f"{ROOT_PATH + '/config.yml'}"
        )
    return value

SCOS_OIDC_ENDPOINT: str = scos_config(
    "SCOS_OIDC_ENDPOINT",
    "https://auth-test.online.edu.ru/realms/portfolio"
)
SCOS_BASE_URL: str = scos_config(
    "SCOS_BASE_URL",
    "https://test.online.edu.ru"
)
SCOS_X_CN_UUID: str = scos_config(
    "SCOS_X_CN_UUID",
    echo = True
)
SCOS_PARTNER_ID: str = scos_config(
    "SCOS_PARTNER_ID",
    echo = True
)
SCOS_HTTPS_ENABLE: str = scos_config(
    "SCOS_HTTPS_ENABLE",
    True
)
SCOS_HTTPS_PROXY: str = scos_config(
    "SCOS_HTTPS_PROXY"
)



hooks.Filters.ENV_PATCHES.add_items(
    [
        (
            "cms-env",
            f"SCOS_OIDC_ENDPOINT: \"{SCOS_OIDC_ENDPOINT}\""
        ),
        (
            "cms-env",
            f"SCOS_BASE_URL: \"{SCOS_BASE_URL}\""
        ),
        (
            "cms-env",
            f"SCOS_X_CN_UUID: \"{SCOS_X_CN_UUID}\""
        ),
        (
            "cms-env",
            f"SCOS_PARTNER_ID: \"{SCOS_PARTNER_ID}\""
        ),
        (
            "cms-env",
            f"SCOS_HTTPS_ENABLE: \"{SCOS_HTTPS_ENABLE}\""
        ),
        (
            "cms-env",
            f"SCOS_HTTPS_PROXY: \"{SCOS_HTTPS_PROXY}\""
        ),
    ]
)

hooks.Filters.ENV_PATCHES.add_items([
    (
        "lms-env", textwrap.dedent("""
            THIRD_PARTY_AUTH_BACKENDS: [
                "social_core.backends.google.GoogleOAuth2",
                "cms.djangoapps.scos.utils.auth.SCOSAuthBackend"
            ]
        """).strip()
    ),
    (
        "lms-env-features", textwrap.dedent("""
            ENABLE_THIRD_PARTY_AUTH: true
        """).strip()
    ),
    (
        "openedx-dockerfile-post-python-requirements", textwrap.dedent("""
            RUN $PIP_COMMAND install git+https://github.com/cdot-ssau/tutor-scos
        """).strip()
    ),
    (
        "mfe-lms-common-settings", textwrap.dedent("""
            MFE_CONFIG["CMS_BASE_URL"] = CMS_ROOT_URL
            FRONTEND_SITE_CONFIG["commonAppConfig"]["CMS_BASE_URL"] = CMS_ROOT_URL
        """).strip()
    ),
    (
        "mfe-env-config-buildtime-definitions", SCOS_LOADERS
    ),
    (
        "mfe-site-custom-app-definitions", SCOS_LOADERS
    ),
])

EXTERNAL_SCRIPTS.add_items([
    ("catalog", "SCOSCatalogLoader"),
])
