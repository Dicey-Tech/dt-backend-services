FROM python:3.8
LABEL maintainer="Sofiane Bebert <s.bebert@diceytech.co.uk>"

RUN apt-get update && export DEBIAN_FRONTEND=noninteractive \
    # Remove imagemagick due to https://security-tracker.debian.org/tracker/CVE-2019-10131
    && apt-get purge -y imagemagick imagemagick-6-common

ENV DJANGO_SETTINGS_MODULE=classroom.settings.local

ENV PYTHONUNBUFFERED 1