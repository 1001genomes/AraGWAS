# Dockerfile to run AraGWAS

FROM python:3
MAINTAINER uemit.serenr@gmi.oeaw.ac.at


# add postgres dependencies
#RUN apk add --no-cache postgresql-dev gcc python3-dev musl-dev linux-headers libffi-dev
RUN apt-get update && apt-get install hdf5-helpers

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
RUN chmod 755 web-entrypoint.sh && chmod 755 wait-for-it.sh

RUN addgroup --system aragwas && adduser --system --group aragwas
RUN chown aragwas -R /srv/web/

USER aragwas

ENTRYPOINT /srv/web/web-entrypoint.sh
