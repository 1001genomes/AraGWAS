#!/bin/bash

mkdir -p "GENOTYPE_DATA"
cd GENOTYPE_DATA

GFF3_FILE="Araport11_GFF3_genes_transposons.201606.gff"
GO_TERM_FILE="ATH_GO_GOSLIM.txt"
SNPEFF_FILE="snpeff.csv"

# Download genes file
if [ ! -f $GFF3_FILE ]; then
    echo "Downloading GFF3 file"
    curl -O http://www.arabidopsis.org/download_files/Genes/Araport11_genome_release/${GFF3_FILE}.gz
    gunzip ${GFF3_FILE}.gz
fi

# Download GO Ontology file
if [ ! -f $GO_TERM_FILE ]; then
    echo "Downloading GO TERM file"
    curl -O http://www.arabidopsis.org/download_files/GO_and_PO_Annotations/Gene_Ontology_Annotations/${GO_TERM_FILE}.gz
    gunzip ${GO_TERM_FILE}.gz
fi

# Download SNPEff file
if [ ! -f $SNPEFF_FILE ]; then
    echo "Downloading SNPEFF file file"
    curl -O http://aragwas.1001genomes.org/${SNPEFF_FILE}.gz
    gunzip ${SNPEFF_FILE}
fi

cd ..
echo "Starting import..."
./manage.py setup_es GENOTYPE_DATA/${GFF3_FILE} GENOTYPE_DATA/${GO_TERM_FILE} GENOTYPE_DATA/${SNPEFF_FILE}
