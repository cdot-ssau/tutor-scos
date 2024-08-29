# Плагин для интеграции сборки OpenedX [Tutor](https://docs.tutor.edly.io/) с [ГИС СЦОС](https://tech.online.edu.ru/)

## Установка плагина

```bash
pip install git+https://github.com/cdot-ssau/tutor-scos
```

## Подключение

```bash
tutor plugins enable scos
tutor config save
tutor local launch
```

## Вносимые изменения

### Подключение авторизации через СЦОС

- In lms.yml, change the value of FEATURES > ENABLE_THIRD_PARTY_AUTH to true.
