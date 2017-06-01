from elasticsearch import Elasticsearch, helpers
from aragwas.settings import ES_HOST
from .parsers import parse_snpeff
import logging
import json
import os

# Get an instance of a logger
logger = logging.getLogger(__name__)

es = Elasticsearch([ES_HOST],timeout=60)
BULK_INDEX_COUNT = 1000
ES_TEMPLATE_PATH = os.path.join(os.path.join(os.path.dirname(__file__),'es_templates'))

def check_server():
    """Check if server is running"""
    return es.ping()

def check_genotype_data():
    """Checks if the genotype data is fully indexed"""
    GENE_COUNT_TO_CHECK = 33341
    SNP_COUNT_TO_CHECK = 10700998
    gene_count = es.count('genotype',doc_type='genes')['count']
    snps_count = es.count('genotype',doc_type='snps')['count']
    if gene_count != GENE_COUNT_TO_CHECK:
        raise Exception('Only %s instead of %s genes found' % (gene_count,GENE_COUNT_TO_CHECK))
    if snps_count != SNP_COUNT_TO_CHECK:
        raise Exception('Only %s instead of %s SNPs found' % (snps_count,SNP_COUNT_TO_CHECK))


def check_indices():
    """Initializes the ES indices"""

    # check if index exists
    indices_exists = es.indices.exists(
        'aragwas') or es.indices.exists('geno_*', allow_no_indices=False)
    if indices_exists:
       raise Exception('Indices already exist. Delete before you continue')

    # create the indices
    with open(os.path.join(ES_TEMPLATE_PATH, 'es_aragwas.json'), 'r') as fh:
        aragwas_settings = json.load(fh)

    with open(os.path.join(ES_TEMPLATE_PATH,'es_genotype.json'), 'r') as fh:
        genotype_settings = json.load(fh)

    # put index template
    es.indices.put_template('aragwas', aragwas_settings)
    # put index template
    es.indices.put_template('geno_*', genotype_settings)

def index_associations(study, associations):
    """indexes associations"""



def index_genes(genes):
    """Indexes the genes"""
    num_genes = len(genes)
    documents = [{'_index':'geno_%s' % gene['chr'].lower(),'_type':'genes','_id':gene_id,'_source':gene} for gene_id, gene in genes.items()]
    success, errors = helpers.bulk(es,documents,chunk_size=10000,stats_only=True)
    return success, errors


def index_snps(snpeff_file):
    """indexes the snps"""
    success, errors = helpers.bulk(es,_get_snps_document(snpeff_file), stats_only=True, chunk_size=10000)
    return success, errors

def _get_association_document(study, top_associations):
    for assoc in top_associations:
        source = assoc.copy()
        source['study'] = study
        yield {
            '_index':'aragwas','_type':'associations','_id': '%s_%s_%s' % (study.pk, assoc['chr'], assoc['position']),'_source':source
        }

def _get_snps_document(snpeff_file):
    with open(snpeff_file,'r') as content:
        is_custom_snp_eff = True
        for row in content:
            if row[0] == '#':
                is_custom_snp_eff = False
                continue
            fields = row.split("\t")
            snp = parse_snpeff(fields, is_custom_snp_eff)
            action = {'_index':'geno_%s' % snp['chr'].lower(),'_type':'snps','_id':snp['position'],'_source':snp}
            yield action
