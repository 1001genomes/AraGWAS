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

## Reindexing
In the case of changes in the elasticsearch template, reindexing must be performed. The procedure includes loading all necessary libraries from the project folder and erase the index using.

`es.indices.delete(index='aragwas')`

Where the name of the index can also be `geno_chrX` for the genotypes index.
Once this is done, the new index can be created by loading the json template and creating the new index:

```
aragwas_settings = json.load(open(path_to_template, 'r'))
es.indices.put_template('aragwas', aragwas_settings)
```

Then, the index can be populated by the individual comments
```
./manage.py index_study --permutations path_to_permutations_file
```
