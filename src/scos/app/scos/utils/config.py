import codecs
import os
from importlib import import_module
import yaml

CONFIG_FILE = os.environ["CMS_CFG"]
with codecs.open(CONFIG_FILE, encoding="utf-8") as f:
    __config__ = yaml.safe_load(f)
    SCOS_BASE_URL = __config__["SCOS_BASE_URL"]
    SCOS_X_CN_UUID = __config__["SCOS_X_CN_UUID"]
    SCOS_PARTNER_ID = __config__["SCOS_PARTNER_ID"]
    SCOS_ENABLE_HTTPS = __config__["SCOS_HTTPS_ENABLE"]
    SCOS_HTTPS_PROXY = __config__["SCOS_HTTPS_PROXY"]

SETTINGS = import_module(os.environ["DJANGO_SETTINGS_MODULE"])
LMS_BASE_URL = SETTINGS.LMS_BASE

if SCOS_ENABLE_HTTPS == "False":
    LMS_URL = f"http://{LMS_BASE_URL}"
else:
    LMS_URL = f"https://{LMS_BASE_URL}"
