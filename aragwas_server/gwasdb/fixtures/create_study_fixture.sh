#!/bin/bash

if [ -z "$1" ]; then
    echo 'Pass in the study id from AraPheno'
    exit 1
fi

curl https://arapheno.1001genomes.org/rest/study/$1/phenotypes.json | jq '[.[] | {model: "gwasdb.study", pk:(.phenotype_id + 4),fields: {name:(.name + "raw_250k_amm"), transformation: "raw", genotype:1,phenotype: .phenotype_id, method:"amm",publication: "http://www.nature.com/nature/journal/v465/n7298/full/nature08800.html" , easygwas_link:"https://arapheno.1001genomes.org/phenotype/\(.phenotype_id)"}}]'