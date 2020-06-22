# https://github.com/docker-library/python/blob/1d59eb2dd813c64891bf554a8ea01754aba25816/3.6/alpine3.6/Dockerfile
FROM python:3.6-alpine3.7

ENV PYTHONUNBUFFERED 1
ENV GEVENT_SUPPORT True
ENV PYTHONPATH /home/python:/home/python/debug-eggs/pycharm-debug-py3k.egg

# Libraries required for order installation
RUN apk upgrade --update && \
    apk add --no-cache --update --virtual .no-persistent-deps g++ gcc libxml2 libxml2-dev libxslt-dev libffi-dev openssl-dev && \
    apk add --no-cache --update --virtual .persistent-deps && \
    apk add --no-cache --update --virtual .persistent-tools libxslt libevent curl vim

RUN mkdir /home/python
WORKDIR /home/python

COPY requirements.txt ./
RUN pip3 install -r requirements.txt

# Free libraries required for order installation
RUN apk del .no-persistent-deps

CMD ["sh", "-c", "python manage.py migrate && python manage.py loaddata initial_data.json && python manage.py runserver 0.0.0.0:8000"]
