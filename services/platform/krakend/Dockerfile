FROM krakend:2.10 as builder

# Аргумент для выбора окружения (dev, prod и т.д.). По умолчанию 'development'.
# Название должно совпадать с именем файла в config/settings (например, development.json)
ARG ENV=local
ARG SERVICE_PATH=/services/platform/krakend

# Устанавливаем рабочую директорию
WORKDIR /etc/krakend

# Копируем шаблоны и настройки
COPY ${SERVICE_PATH}/krakend.tmpl .
COPY ${SERVICE_PATH}/config/settings ./settings/
COPY ${SERVICE_PATH}/config/templates ./templates/

# Запускаем проверку и генерацию krakend.json
# KrakenD использует ENV для выбора нужного блока настроек в шаблоне

RUN FC_ENABLE=1 \
    FC_OUT=/tmp/krakend.json \
    FC_SETTINGS=/etc/krakend/settings/${ENV} \
    FC_TEMPLATES=/etc/krakend/templates \
    krakend check -d -t -c krakend.tmpl

RUN krakend check -c /tmp/krakend.json || (cat /tmp/krakend.json && exit 1)

# Этап 2: Финальный образ
FROM krakend:2.10

# Обновляем пакеты для безопасности
RUN apk upgrade --no-cache --no-interactive

# Копируем скомпилированную конфигурацию из этапа сборки
COPY --from=builder --chown=krakend:nogroup /tmp/krakend.json /etc/krakend/krakend.json