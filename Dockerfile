FROM python:3 as django
RUN useradd --uid=10372 -ms /bin/bash aragwas && mkdir -p /srv/web &&  mkdir -p /srv/static && chown aragwas:aragwas /srv/static && chown aragwas:aragwas /srv/web
COPY aragwas_server/requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt && pip install gunicorn
# copy webservice code
COPY --chown=aragwas:aragwas aragwas_server /srv/web
WORKDIR /srv/web
COPY --chown=aragwas:aragwas entrypoint.sh write_version.sh wait-for-it.sh ./

RUN chmod 755 entrypoint.sh wait-for-it.sh write_version.sh

ARG GIT_BRANCH
ENV GIT_BRANCH $GIT_BRANCH

ARG GIT_COMMIT
ENV GIT_COMMIT $GIT_COMMIT

ARG BUILD_NUMBER
ENV BUILD_NUMBER $BUILD_NUMBER

ARG BUILD_URL
ENV BUILD_URL $BUILD_URL

RUN /srv/web/write_version.sh /srv/web/gwasdb/__init__.py

USER aragwas


FROM django as aragwas-worker
ENTRYPOINT ["/srv/web/entrypoint.sh", "aragwas-worker"]

FROM node:11-alpine AS builder
WORKDIR /app
COPY aragwas_ui/package.json aragwas_ui/package-lock.json /app/
RUN npm install
COPY aragwas_ui /app
RUN npm run build


FROM django as aragwas-backend
COPY --chown=aragwas:aragwas --from=builder /app/dist/static /srv/web/gwasdb/static
COPY --chown=aragwas:aragwas --from=builder /app/dist/index.html /srv/web/gwasdb/templates/index.html
ENTRYPOINT ["/srv/web/entrypoint.sh", "aragwas-backend"]

