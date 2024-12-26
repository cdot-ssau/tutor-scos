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

Настройки для подключения к защищенному контуру:

```yaml
SCOS_BASE_URL: https://tls.online.edu.ru
SCOS_OIDC_ENDPOINT: https://auth.online.edu.ru/realms/portfolio
```

- Настройки https. Применяется при формировании адресных строк для ресурсов платформы, по умолчанию `true`. Задается отдельно от настроек https платформы, например для случаев когда используется реверс прокси для которого настроен https, а для платформы https отключен. Значение `false` устанавливается если https вообще не используется, например если для запуска платформы использовалась команда `tutor dev launch`.

```yaml
SCOS_HTTPS_ENABLE: true
```

- Настройки https прокси. Указывается в [формате](https://requests.readthedocs.io/en/latest/user/advanced/#proxies) `http://<user>:<password>@<id address>:<port>/`.

```yaml
SCOS_HTTPS_PROXY: http://user:password@10.10.10.10:80/
```

### Настройка авторизации

В административном разделе платформы `https://<платформа>/admin/third_party_auth/oauth2providerconfig/` необходимо создать конфигурацию для провайдера авторизации СЦОС.

- Backend name: scos.

- Client ID и Client Secret предоставляются техподдержкой СЦОС.

## Поддержка собственных тем OpenedX

Плагин добавляет виджет отзывов СЦОС в описание курса только для стандартного шаблона `/openedx/edx-platform/lms/templates/courseware/course_about.html`. Если используется собственная тема переопределяющая этот шаблон, то необходимо добавить блок с отзывами в шаблон course_about.html этой темы, см. модуль `scos.utils.patch`.
