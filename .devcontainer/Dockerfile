FROM python:3.8
LABEL maintainer="Sofiane Bebert <s.bebert@diceytech.co.uk>"

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    # Remove imagemagick due to https://security-tracker.debian.org/tracker/CVE-2019-10131
    && apt-get purge -y imagemagick imagemagick-6-common

ENV PYTHONUNBUFFERED 1
ARG APP_USER_ID=1000
RUN useradd --home-dir /code --create-home --shell /bin/bash --uid ${APP_USER_ID} vscode
USER ${APP_USER_ID}