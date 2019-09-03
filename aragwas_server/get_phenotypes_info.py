# Quick script to fetch HDF5 study information from AraGWAS
# This is run by the prepare_download.sh script
# Assumption: this must be run once the studies of interest are already in AraGWAS
import os
import argparse
import requests
import numpy as np
# import pandas as pd

def get_accession_matrix(phenotype_id):
    r = requests.get('https://arapheno.1001genomes.org:443/rest/phenotype/{}/values.json'.format(phenotype_id))
    js = r.json()
    accession_matrix = []
    for j in js:
        accession_matrix.append([j["accession_id"],j["accession_name"], j["accession_longitude"], j["accession_latitude"], j["accession_country"], j["phenotype_value"]])
    return np.asarray(accession_matrix)
