# Dockerfile to run AraGWAS

FROM node:latest
MAINTAINER uemit.serenr@gmi.oeaw.ac.at

RUN mkdir /srv/aragwas_ui
WORKDIR /srv/aragwas_ui

COPY package.json .

RUN npm install

RUN npm config set prefix "$(pwd)/node_modules"

RUN export NODE_PATH=/srv/aragwas_ui/node_modules/
