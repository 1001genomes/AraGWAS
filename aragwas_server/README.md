# AraGWAS backend

The AraGWAS backend is a django app that serves as a REST endpoint for the AraGWAS frontend.

## Installation

`pip install -r requirements.txt`

## Prepare Elasticseach DB and and start RabbitMQ

Before the AraGWAS backend can be used, the RabbitMQ server must be started and the genotypes need to be indexed in the elasticserach database

To make it easy to get started, the `docker-compose.yml` file will start both services.

`docker-compose up -d elasticsearch1 amqp1`

To get the genotype information indexed in the ES database, run the `init_elasticsearch.sh` script. This has to be done only once.

`./init_elasticserach.sh`

This will download the data and start the indexing proceess, which can take a while (~ 15 minutes).
Afterwards you can start the backend with the command below.

## Development

`./manage runserver`

