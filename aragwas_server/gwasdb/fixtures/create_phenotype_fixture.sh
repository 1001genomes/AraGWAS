#!/bin/bash

if [ -z "$1" ]; then
    echo 'Pass in the study id from AraPheno'
    exit 1
fi

curl https://arapheno.1001genomes.org/rest/study/$1/phenotypes.json | jq '[.[] | {model: "gwasdb.phenotype", pk:.phenotype_id,fields: {name:.name, description:.scoring, date:.integration_date, arapheno_link:"https://arapheno.1001genomes.org/phenotype/\(.phenotype_id)"}}]'