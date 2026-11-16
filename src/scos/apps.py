from django.apps import AppConfig


class ScosConfig(AppConfig):
    name = "scos"
    verbose_name = "ГИС СЦОС"

    plugin_app = {
        "url_config": {
            "cms.djangoapp": {
                "namespace": "scos",
                "regex": r"^scos/",
                "relative_path": "urls",
            },
        },
        "settings_config": {
            "lms.djangoapp": {
                "common": {"relative_path": "settings.common"},
            },
            "cms.djangoapp": {
                "common": {"relative_path": "settings.common"},
            },
        },
    }
