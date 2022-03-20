FROM debian:bullseye-slim

# Set the locale
ENV LANG C.UTF-8
ENV LANGUAGE C
ENV LC_ALL C.UTF-8

RUN apt-get update && \
  apt-get -y --no-install-recommends install \
    make dbus gpg python3-pip \
    pypass python3-gi python3-secretstorage python3-click python3-decorator python3-simplejson \
    pycodestyle python3-coverage python3-pytest python3-pytest-asyncio && \
  pip3 install --no-cache-dir dbus-next && \
  apt-get purge -y --autoremove python3-pip && \
  apt-get clean && \
  rm -rf /var/lib/apt/lists/*

WORKDIR /pass_secret_service

ADD . /pass_secret_service

CMD make style coverage
