from __future__ import annotations

import os
import os.path
import shutil
from glob import glob
from typing import Union

import appdirs
import pkg_resources
from tutor import hooks, fmt, serialize
from tutor import config as tutor_config
from tutor.types import Config
from tutor.__about__ import __app__
from .__about__ import __version__



ROOT_PATH: str = (os.path.expanduser(os.environ.get("TUTOR_ROOT", ""))
    or appdirs.user_data_dir(__app__)
)
SCOS_BUILD: str = pkg_resources.resource_filename("scos", "app")
SCOS_TEMPLATES: str = pkg_resources.resource_filename("scos", "templates")
SCOS_PATCHES: str = pkg_resources.resource_filename("scos", "patches")



hooks.Filters.CONFIG_DEFAULTS.add_items(
    [
        ("SCOS_VERSION", __version__),
    ]
)



# Копируем Django приложение и дополнительные модули СЦОС в папку с Dockerfile openedX
shutil.copytree(
    os.path.join(SCOS_BUILD, "scos"),
    os.path.join(ROOT_PATH, "env/build/openedx/scos"),
    dirs_exist_ok=True
)



CONFIG_MOD: dict = {
        "OPENEDX_EXTRA_PIP_REQUIREMENTS": [
            "python-jose>=3.0.0",
        ],
}

@hooks.Actions.PLUGIN_LOADED.add()
def add_scos_config_mod_to_environ(plugin: str) -> None:
    """
    Add scos config modifications to os.environ
    """
    if plugin != "scos":
        return
    env_var: str = os.environ.get("CONFIG_MOD")
    if env_var is None:
        os.environ.update({"CONFIG_MOD": str(CONFIG_MOD)})
    else:
        env_mod: dict = serialize.parse(env_var)
        for key, value in CONFIG_MOD.items():
            if not key in env_mod:
                env_mod.update({key: value})
            else:
                if env_mod[key] != value:
                    env_mod[key] += [
                        e for e in value if e not in env_mod[key]
                    ]
        os.environ.update({"CONFIG_MOD": str(env_mod)})

@hooks.Actions.PLUGINS_LOADED.add()
def write_changes_to_config():
    """
    Add config modifications from os.environ to config 
    """
    config: Config = tutor_config.load_minimal(ROOT_PATH)
    env_var: str = os.environ.get("CONFIG_MOD")
    if env_var is None:
        return
    env_mod: dict = serialize.parse(env_var)
    config_mod: bool = False
    for key, value in env_mod.items():
        if not key in config:
            config.update({key: value})
            config_mod = True
        else:
            if not set(value) <= set(config[key]):
                config[key] += [
                    e for e in value if e not in config[key]
                ]
                config_mod = True
    if config_mod:
        tutor_config.save_config_file(ROOT_PATH, config)



def check_defaults(key: str, default: str = "") -> str:
    """
    Проверяем изменены ли настройки по умолчанию
    """
    config: Config = tutor_config.load_minimal(ROOT_PATH)
    value: Union[str, None] = config.get(key)
    if value is None:
        value = default
        config.update({key: value})
        tutor_config.save_config_file(ROOT_PATH, config)
    if value == default:
        fmt.echo_info(
            f"Обновите переменную {key} в конфигурационном файле:\n"
            f"{ROOT_PATH + '/config.yml'}"
        )
    return value

SCOS_OIDC_ENDPOINT: str = check_defaults(
    "SCOS_OIDC_ENDPOINT",
    "https://auth-test.online.edu.ru/realms/portfolio"
)
SCOS_BASE_URL: str = check_defaults(
    "SCOS_BASE_URL",
    "https://test.online.edu.ru"
)
SCOS_X_CN_UUID: str = check_defaults(
    "SCOS_X_CN_UUID",
)
SCOS_PARTNER_ID: str = check_defaults(
    "SCOS_PARTNER_ID",
)



hooks.Filters.ENV_PATCHES.add_items(
    [
        (
            "lms-env",
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
    ]
)



for path in glob(os.path.join(SCOS_PATCHES, "*")):
    with open(path, encoding="utf-8") as patch_file:
        hooks.Filters.ENV_PATCHES.add_item(
            (os.path.basename(path), patch_file.read())
        )
