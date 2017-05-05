# Dockerfile to run AraGWAS

FROM python:3-alpine
MAINTAINER uemit.serenr@gmi.oeaw.ac.at


# add postgres dependencies
#RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev linux-headers libffi-dev
RUN apk --no-cache --update --repository http://dl-cdn.alpinelinux.org/alpine/edge/testing add musl-dev linux-headers g++ hdf5-dev python-dev py-pip

# woraround for missing xlocale.h
RUN ln -s /usr/include/locale.h /usr/include/xlocale.h
# copy file and install webservice requirements
COPY requirements.txt .
RUN pip install -r requirements.txt
#RUN pip install uWSGI

# pseudo install config file
#RUN mkdir /etc/platinum
#COPY webservice/instance/config.py /etc/platinum/config

# copy webservice code
COPY . /srv/web
WORKDIR /srv/web


COPY web-entrypoint.sh .
RUN chmod 755 web-entrypoint.sh

RUN addgroup -S aragwas && adduser -S -g aragwas aragwas
RUN chown aragwas -R /srv/web/

USER aragwas

ENTRYPOINT /srv/web/web-entrypoint.sh
