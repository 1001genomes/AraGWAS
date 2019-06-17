# Dockerfile to run AraGWAS

FROM node:latest
MAINTAINER uemit.serenr@gmi.oeaw.ac.at

RUN mkdir /srv/aragwas_ui
WORKDIR /srv/aragwas_ui

COPY package.json package-lock.json ./

RUN npm install


