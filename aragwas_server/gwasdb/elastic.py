from elasticsearch import Elasticsearch, helpers
from elasticsearch_dsl import Search, Q, A

from aragwas.settings import ES_HOST
from gwasdb import serializers
from .parsers import parse_snpeff, parse_lastel
import logging
import json
import os
import numpy as np
import re
import operator
import datetime

GENE_ID_PATTERN = re.compile('^[a-z]{2}([\\d]{1})G\\w+$', re.IGNORECASE)

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

def load_snps_by_region(chrom, start, end):
    """Retrieve snp information by region"""
    index = 'geno_%s'
    if len(chrom) > 3:
        index = index % chrom
    else:
        index = index % 'chr' + chrom
    search_snps = Search().using(es).doc_type('snps').index(index).filter("range", position={"lte": end, "gte":start})
    return {snp.position: snp.to_dict() for snp in search_snps.scan() }

def load_snps(chrom, positions):
    """Retrieve snp information"""
    index = 'geno_%s'
    if len(chrom) > 3:
        index = index % chrom
    else:
        index = index % 'chr' + chrom
    if isinstance(positions, np.ndarray):
        pos = positions.tolist()
    else:
        pos = positions
    if len(pos) == 0:
        return {}
    resp = es.mget(body={'ids':pos}, index=index, doc_type='snps')
    return {doc['_id']: doc['_source'] if doc['found'] else {} for doc in resp['docs'] }


def autocomplete_genes(term):
    """For autocomplete searches"""
    resp = es.search(index='genotype',doc_type='genes',_source=["suggest", "positions","strand","chr","type"],
        body={"suggest": {
                "gene-suggest": {
                    "prefix":term,
                    "completion": {
                        "field": "suggest"
                    }
                }
        }})
    return [{'id':option['_id'], 'name': option['text'],'strand': option['_source']['strand'], 'chr': option['_source']['chr'], 'type': option['_source']['type'], 'positions':option['_source']['positions']} for option in resp['suggest']['gene-suggest'][0]['options']]


def load_gene_by_id(id):
    """Retrive genes by id"""
    matches = GENE_ID_PATTERN.match(id)
    if not matches:
        raise Exception('Wrong Gene ID %s' % id)
    chrom = matches.group(1)
    doc = es.get('geno_chr%s' % chrom, id, doc_type='genes', _source=['name','chr','positions','type','strand', 'isoforms'], realtime=False)
    if not doc['found']:
        raise Exception('Gene with ID %s not found' %id)
    gene = doc['_source']
    gene['id'] = doc['_id']
    return gene

def load_gene_associations(id):
    """Retrive associations by neighboring gene id"""
    matches = GENE_ID_PATTERN.match(id)
    if not matches:
        raise Exception('Wrong Gene ID %s' % id)
    chrom = matches.group(1)
    asso_search = Search(using=es).doc_type('snps').source(exclude=['isoforms','GO'])
    q = Q({'nested':{'path':'snps.annotations', 'query':{'match':{'snps.annotations.gene_name':id}}}})
    asso_search = asso_search.filter(q).sort('score')
    results = asso_search[0:min(500, asso_search.count())].execute()
    associations = results.to_dict()['hits']['hits']
    return [{association['_id']: association['_source']} if association['found'] else {} for association in associations]

def load_gene_snps(id):
    """Retrive associations by neighboring gene id"""
    snp_search = Search(using=es).doc_type('snps')
    q = Q({'nested':{'path':'annotations', 'query':{'match':{'annotations.gene_name':id}}}})
    snp_search = snp_search.filter(q).sort('position')
    results = snp_search[0:min(500, snp_search.count())].execute()
    associations = results.to_dict()['hits']['hits']
    return [{association['_id']: association['_source']} for association in associations]

def get_top_genes():
    """Retrive associations by neighboring gene id"""
    s = Search(using=es, doc_type='associations')
    agg = A("terms", field="snp.gene_name")
    s.aggs.bucket('gene_count', agg)
    agg_results = s.execute().aggregations.gene_count.buckets
    return agg_results

def get_top_genes_and_snp_type_for_study(study_id):
    """Retrive associations by neighboring gene id"""
    s = Search(using=es, doc_type='associations')
    s = s.filter(Q('bool', should=[Q('term', study__id=study_id)]))
    s = s.filter('term', overFDR='T')
    agg_genes = A("terms", field="snp.gene_name")
    agg_snp_type = A("terms", field="snp.coding")
    s.aggs.bucket('gene_count', agg_genes)
    s.aggs.bucket('snp_type_count', agg_snp_type)
    agg_results = s.execute().aggregations
    return agg_results.gene_count.buckets, agg_results.snp_type_count.buckets


def index_associations(study, associations, thresholds):
    """indexes associations"""
    lowest_threshold = min(filter(None, [thresholds['bonferoni_threshold05'], thresholds['bonferoni_threshold01'], thresholds['bh_threshold']]))
    thresholds = [{'name': key, 'value': val} for key, val in thresholds.items() ]
    # first filter by chr to fetch annotations
    associations.sort(order = 'chr')
    annotations = {}
    for chrom in range(1, 6):
        chrom_pos = associations['position'][np.where(associations['chr'] == str(chrom))]
        annotations[str(chrom)] = load_snps(str(chrom),chrom_pos)
    documents = []
    for assoc in associations:
        _id = '%s_%s_%s' % (study.pk, assoc['chr'], assoc['position'])
        study_data = serializers.EsStudySerializer(study).data
        study_data['thresholds'] = thresholds
        _source = {'mac': int(assoc['mac']), 'maf': float(assoc['maf']), 'score': float(assoc['score']), 'created': datetime.datetime.now(),'study':study_data, 'overFDR': bool(assoc['score'] > lowest_threshold)}
        snp = annotations[assoc['chr']].get(str(assoc['position']), None)
        if snp:
            _source['snp']  = snp
        documents.append({'_index':'aragwas','_type':'associations','_id': _id, '_source': _source })
    if len(documents) == 0:
        return 0,0
    success, errors = helpers.bulk(es,documents, chunk_size=1000, stats_only=True)
    return success, errors

def load_filtered_top_associations(filters, start=0, size=50):
    """Retrieves top associations and filter them through the tickable options"""
    s = Search(using=es, doc_type='associations')
    s = s.sort('-score')
    if 'score' in filters:
        s = s.filter('range', score={'gte': filter})
    if 'chr' in filters and len(filters['chr']) > 0 and len(filters['chr']) < 5:
        s = s.filter(Q('bool', should=[Q('term', snp__chr=chrom if len(chrom) > 3 else 'chr%s' % chrom) for chrom in filters['chr']]))
    if 'maf' in filters and len(filters['maf']) > 0 and len(filters['maf']) < 4:
        maf_filters = []
        for maf in filters['maf']:
            maf = maf.split('-')
            if len(maf) > 1:
                maf_filters.append(Q('range', maf={'lte': float(maf[1])/100,'gte':float(maf[0])/100}))
            else:
                if maf[0] == '1':
                    maf_filters.append(Q('range', maf={'lte':float(maf[0])/100}))
                else:
                    maf_filters.append(Q('range', maf={'gte':float(maf[0])/100}))
        s = s.filter(Q('bool',should = maf_filters))
    if 'annotation' in filters and len(filters['annotation']) > 0 and len(filters['annotation']) < 4:
        annot_filter = [Q('term', snp__annotations__effect=anno) for anno in filters['annotation']]
        s = s.filter(Q('nested', path='snp.annotations', query=Q('bool', should=annot_filter)))
    if 'type' in filters and len(filters['type'])==1:
        s = s.filter('term', snp__coding='T' if filters['type'][0] == 'genic' else 'F')
    if 'study_id' in filters and len(filters['study_id']) > 0:
        s = s.filter(Q('bool', should=[Q('term',study__id = study_id) for study_id in filters['study_id']]))
    if 'phenotype_id' in filters and len(filters['phenotype_id']) > 0:
        s = s.filter(Q('bool', should=[Q('term',study__phenotype__id = phenotype_id) for phenotype_id in filters['phenotype_id']]))
    if 'genotype_id' in filters and len(filters['genotype_id']) > 0:
        s = s.filter(Q('bool', should=[Q('term',study__genotype__id = genotype_id) for genotype_id in filters['genotype_id']]))
    if 'start' in filters:
        s = s.filter('range', snp__position={'gte': int(filters['start'])})
    if 'end' in filters:
        s = s.filter('range', snp__position={'lte': int(filters['end'])})
    s = s[start:start+size]
    print(json.dumps(s.to_dict()))
    result = s.execute()
    associations = result['hits']['hits']
    return [association['_source'].to_dict() for association in associations], result['hits']['total']

def load_filtered_top_associations_search_after(filters, search_after = ''):
    """Retrieves top associations and filter them through the tickable options"""
    s = Search(using=es, doc_type='associations')
    s = s.sort('-score', '_uid')
    if 'score' in filters:
        s = s.filter('range', score={'gte': filter})
    if 'chr' in filters and len(filters['chr']) > 0 and len(filters['chr']) < 5:
        s = s.filter(Q('bool', should=[Q('term', snp__chr=chrom if len(chrom) > 3 else 'chr%s' % chrom) for chrom in filters['chr']]))
    if 'maf' in filters and len(filters['maf']) > 0 and len(filters['maf']) < 4:
        maf_filters = []
        for maf in filters['maf']:
            maf = maf.split('-')
            if len(maf) > 1:
                maf_filters.append(Q('range', maf={'lte': float(maf[1])/100,'gte':float(maf[0])/100}))
            else:
                if maf[0] == '1':
                    maf_filters.append(Q('range', maf={'lte':float(maf[0])/100}))
                else:
                    maf_filters.append(Q('range', maf={'gte':float(maf[0])/100}))
        s = s.filter(Q('bool',should = maf_filters))
    if 'annotation' in filters and len(filters['annotation']) > 0 and len(filters['annotation']) < 4:
        annot_filter = [Q('term', snp__annotations__effect=anno) for anno in filters['annotation']]
        s = s.filter(Q('nested', path='snp.annotations', query=Q('bool', should=annot_filter)))
    if 'type' in filters and len(filters['type'])==1:
        s = s.filter('term', snp__coding='T' if filters['type'][0] == 'genic' else 'F')
    if 'study_id' in filters and len(filters['study_id']) > 0:
        s = s.filter(Q('bool', should=[Q('term',study__id = study_id) for study_id in filters['study_id']]))
    if 'phenotype_id' in filters and len(filters['phenotype_id']) > 0:
        s = s.filter(Q('bool', should=[Q('term',study__phenotype__id = phenotype_id) for phenotype_id in filters['phenotype_id']]))
    if 'genotype_id' in filters and len(filters['genotype_id']) > 0:
        s = s.filter(Q('bool', should=[Q('term',study__genotype__id = genotype_id) for genotype_id in filters['genotype_id']]))
    if 'start' in filters:
        s = s.filter('range', snp__position={'gte': int(filters['start'])})
    if 'end' in filters:
        s = s.filter('range', snp__position={'lte': int(filters['end'])})
    if search_after != '':
        search_after = parse_lastel(search_after)
        print(search_after)
        s = s.extra(search_after=search_after)
    s = s[0:25]
    print(json.dumps(s.to_dict()))
    result = s.execute()
    associations = result['hits']['hits']
    last_el = result['hits']['hits'][-1]['sort']
    # Transformation needed to saveguard url transmition
    last_el[1] = "-".join(last_el[1].split('#'))
    return [association['_source'].to_dict() for association in associations], result['hits']['total'], last_el


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
