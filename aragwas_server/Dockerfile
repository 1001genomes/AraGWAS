# Dockerfile to run AraGWAS

FROM python:3

RUN apt-get update && apt-get install hdf5-helpers

# copy file and install webservice requirements
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
#RUN pip install uWSGI

# copy webservice code
COPY . /srv/web
WORKDIR /srv/web


COPY web-entrypoint.sh .
RUN chmod 755 web-entrypoint.sh && chmod 755 wait-for-it.sh

RUN addgroup --system aragwas && adduser --system --group aragwas --uid 10372
RUN chown aragwas -R /srv/web/

USER aragwas

ENTRYPOINT ["/srv/web/web-entrypoint.sh"]
CMD ["manage.py"]
