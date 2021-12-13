FROM ubuntu:bionic as app
LABEL maintainer="devops@diceytech.co.uk"


# Packages installed:

# language-pack-en locales; ubuntu locale support so that system utilities have a consistent
# language and time zone.

# python; ubuntu doesnt ship with python, so this is the python we will use to run the application

# python3-pip; install pip to install application requirements.txt files

# libssl-dev; # mysqlclient wont install without this.

# libmysqlclient-dev; to install header files needed to use native C implementation for
# MySQL-python for performance gains.

# If you add a package here please include a comment above describing what it is used for
RUN apt-get update && apt-get -qy install --no-install-recommends \
    language-pack-en \
    locales \
    python3.8 \
    python3-pip \
    libmysqlclient-dev \
    libssl-dev \
    python3-dev && \
    pip3 install --upgrade pip setuptools && \
    rm -rf /var/lib/apt/lists/*

RUN ln -s /usr/bin/pip3 /usr/bin/pip
RUN ln -s /usr/bin/python3 /usr/bin/python

RUN locale-gen en_US.UTF-8
ENV LANG en_US.UTF-8
ENV LANGUAGE en_US:en
ENV LC_ALL en_US.UTF-8
ENV DJANGO_SETTINGS_MODULE classrooms.settings.local

EXPOSE 8180
RUN useradd -m --shell /bin/false app

WORKDIR /edx/app/classroom

# Copy the requirements explicitly even though we copy everything below
# this prevents the image cache from busting unless the dependencies have changed.
COPY requirements/dev.txt /edx/app/classroom/requirements/dev.txt

# Dependencies are installed as root so they cannot be modified by the application user.
RUN pip3 install -r requirements/dev.txt

RUN mkdir -p /edx/var/log

# Code is owned by root so it cannot be modified by the application user.
# So we copy it before changing users.
USER app

# Gunicorn 19 does not log to stdout or stderr by default. Once we are past gunicorn 19, the logging to STDOUT need not be specified.
CMD gunicorn --workers=2 --name classroom -c /edx/app/classroom/classroom/docker_gunicorn_configuration.py --log-file - --max-requests=1000 classrooms.wsgi:application

# This line is after the requirements so that changes to the code will not
# bust the image cache
COPY . /edx/app/classroom

#FROM app as newrelic
#RUN pip install newrelic
#CMD newrelic-admin run-program gunicorn --workers=2 --name classroom -c /edx/app/classroom/classroom/docker_gunicorn_configuration.py --log-file - --max-requests=1000 classrooms.wsgi:application
