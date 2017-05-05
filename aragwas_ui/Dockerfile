# Dockerfile to run AraGWAS

FROM node:latest
MAINTAINER uemit.serenr@gmi.oeaw.ac.at

RUN mkdir /srv/aragwas_ui
WORKDIR /srv/aragwas_ui

COPY package.json .

RUN npm install

COPY . .

VOLUME /srv/aragwas_server/gwasdb/static
VOLUME /srv/aragwas_server/gwasdb/templates

CMD npm run build


