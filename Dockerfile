FROM debian:wheezy

# Set the locale
ENV LANG C.UTF-8
ENV LANGUAGE C
ENV LC_ALL C.UTF-8

RUN apt-get update && apt-get -y install make dbus gpg
RUN apt-get update && apt-get -y install pypass python3-gi python3-pydbus python3-secretstorage python3-click python3-decorator python3-simplejson
RUN apt-get update && apt-get -y install pycodestyle python3-coverage

WORKDIR /pass_secret_service

ADD . /pass_secret_service

CMD make style coverage
