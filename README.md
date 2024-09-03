# Плагин для интеграции сборки OpenedX [Tutor](https://docs.tutor.edly.io/) с [ГИС СЦОС](https://tech.online.edu.ru/)

## Установка плагина

```bash
pip install git+https://github.com/cdot-ssau/tutor-scos
```

## Подключение плагина

- Активация плагина и обновление конфигурации Tutor.

```bash
tutor plugins enable scos
tutor config save
```

- Настройка плагина (см. [Настройка](#настройка)).

- Запуск платформы.

```bash
tutor local launch
```

## Настройка

В конфигурационном файле `~/.local/share/tutor/config.yml` необходимо указать параметры:

- Учетные данные полученные от техподдержки СЦОС (connect@online.edu.ru).

```yaml
SCOS_X_CN_UUID: <уникальный ключ доступа платформы к ГИС СЦОС>
SCOS_PARTNER_ID: <Идентификатор платформы>
```

- Настройки URL СЦОС: основной домен и точка авторизации. По умолчанию указаны настройки для тестового контура, для подключения к защищенному контуру их необходимо изменить.

```yaml
SCOS_BASE_URL: https://test.online.edu.ru
SCOS_OIDC_ENDPOINT: https://auth-test.online.edu.ru/realms/portfolio
```

### Настройка авторизации

В административном разделе платформы `https://<платформа>/admin/third_party_auth/oauth2providerconfig/` необходимо создать конфигурацию для провайдера авторизации СЦОС.

- Backend name: scos.

- Client ID и Client Secret предоставляются техподдержкой СЦОС.

## Поддержка собственных тем OpenedX

Плагин добавляет виджет отзывов СЦОС в описание курса только для стандартного шаблона `/openedx/edx-platform/lms/templates/courseware/course_about.html`. Если используется собственная тема переопределяющая этот шаблон, то необходимо добавить блок с отзывами в шаблон course_about.html этой темы, см. модуль `scos.utils.patch`.
