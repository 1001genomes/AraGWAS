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

from collections import defaultdict

GENE_ID_PATTERN = re.compile('^[a-z]{2}([\\d]{1})G\\w+$', re.IGNORECASE)
es_logger = logging.getLogger('elasticsearch')
es_logger.setLevel(logging.WARNING)

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
    index = _get_index_from_chr(chrom)
    search_snps = Search().using(es).doc_type('snps').index(index).filter("range", position={"lte": end, "gte":start})
    return {snp.position: snp.to_dict() for snp in search_snps.scan() }

def load_snps(chrom, positions):
    """Retrieve snp information"""
    index = _get_index_from_chr(chrom)
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
    # # Potentially, load KO associated phenos if any
    # if return_KOs:
    #     # check if gene has any associated phenotypes
    #     pass
    return gene


def load_associations_by_id(id):
    """Retrieve an association by id"""
    doc = es.get('aragwas', id, doc_type='associations', _source=['overFDR','overPermutation','overPermutation','maf','mac','score', 'snp', 'study'], realtime=False)
    if not doc['found']:
        raise Exception('Associations with ID %s not found' %id)
    association = doc['_source']
    association['id'] = doc['_id']
    return association

def load_ko_associations_by_id(id):
    """Retrieve a KO mutation by id"""
    doc = es.get('aragwas', id, doc_type='ko_associations', _source=['overPermutation','overBonferroni','maf','mac','score', 'gene', 'study'], realtime=False)
    if not doc['found']:
        raise Exception('Associations with ID %s not found' %id)
    association = doc['_source']
    association['id'] = doc['_id']
    return association

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
    """Retrieve top genes"""
    s = Search(using=es, doc_type='associations')
    s = s.filter('term', overPermutation='T')
    s = s.filter(Q('range', mac={'gte': 6}))
    agg = A("terms", field="snp.gene_name")
    s.aggs.bucket('gene_count', agg)
    agg_results = s.execute().aggregations.gene_count.buckets
    return agg_results

def load_filtered_top_genes(filters, start=0, size=50):
    """Retrieves top genes and filter them through the tickable options"""
    # First aggregate over associations
    s = Search(using=es, doc_type='associations')
    if 'chr' in filters and len(filters['chr']) > 0 and len(filters['chr']) < 5:
        s = s.filter(Q('bool', should=[Q('term', snp__chr=chrom if len(chrom) > 3 else 'chr%s' % chrom) for chrom in
                                       filters['chr']]))
    if 'significant' in filters:
        s = s.filter(Q('range', mac={'gte': 6}))
        if filters['significant'][0] == "b":
            s = s.filter('term', overBonferroni='T')
        elif filters['significant'][0] == "p":
            s = s.filter('term', overPermutation='T')
    agg = A("terms", field="snp.gene_name", size="33341") # Need to check ALL GENES for further lists
    s.aggs.bucket('gene_count', agg)
    top_genes = s.execute().aggregations.gene_count.buckets
    genes = []
    for top in top_genes[start:start+size]:
        id = top['key']
        matches = GENE_ID_PATTERN.match(id)
        if not matches:
            continue
        gene = load_gene_by_id(top['key'])
        gene['n_hits'] = top['doc_count']
        genes.append(gene)
    return genes, len(top_genes)

def load_filtered_top_ko_mutations_genes(filters, start=0, size=50):
    """Retrieves top genes according to number of KO mutations and filter them through the tickable options"""
    # First aggregate over associations
    s = Search(using=es, doc_type='ko_associations')
    if 'chr' in filters and len(filters['chr']) > 0 and len(filters['chr']) < 5:
        s = s.filter(Q('bool', should=[Q({'nested':{'path':'gene', 'query':{'match':{'gene.chr':chrom if len(chrom) > 3 else 'chr%s' % chrom}}}}) for chrom in
                                       filters['chr']]))
    if 'significant' in filters:
        s = s.filter(Q('range', mac={'gte': 6}))
        s = s.filter('term', overBonferroni='T') # TODO: change this to permutation once the new indexed scores are in.

    agg = A("terms", field="gene.id", size='33341') # Need to check ALL GENES for further lists
    s.aggs.bucket('genes', 'nested', path='gene').bucket('gene_count', agg) # Need to have a NESTED query
    top_genes = s.execute().aggregations.genes.gene_count.buckets
    # The KO associations are already retrieved, just need to assign them to the right gene.
    association_dict = defaultdict(list)
    for asso in s[0:s.count()].execute().to_dict()['hits']['hits']:
        association_dict[asso['_source']['gene']['name']].append(asso['_source'])
    genes = []
    for top in top_genes[start:start+size]:
        id = top['key']
        matches = GENE_ID_PATTERN.match(id)
        if not matches:
            continue
        gene = load_gene_by_id(top['key'])
        gene['n_hits'] = top['doc_count']
        gene['ko_associations'] = association_dict[top['key']]
        genes.append(gene)
    return genes, len(top_genes)

def get_top_genes_aggregated_filtered_statistics(filters):
    s = Search(using=es, doc_type='genes')
    if 'chr' in filters and len(filters['chr']) > 0 and len(filters['chr']) < 5:
        s = s.filter(Q('bool', should=[Q('term', chr=chrom if len(chrom) > 3 else 'chr%s' % chrom) for chrom in
                                       filters['chr']]))
    agg_chr = A("terms", field="chr")
    s.aggs.bucket('chr_count', agg_chr)
    agg_results = s.execute().aggregations
    return agg_results.chr_count.buckets

def get_top_genes_and_snp_type_for_study(study_id):
    """Retrive associations by neighboring gene id"""
    s = Search(using=es, doc_type='associations')
    s = s.filter(Q('bool', should=[Q('term', study__id=study_id)]))
    s = s.filter('term', overPermutation='T')
    s = s.filter(Q('range', mac={'gte': 6}))
    agg_genes = A("terms", field="snp.gene_name")
    # agg_go_terms = A("terms", field="snp.") NOT DOABLE WITH CURRENT FIELDS IN ES
    agg_snp_type = A("terms", field="snp.coding")
    agg_impact = A(
        {"nested": {"path": "snp.annotations"}, "aggs": {"annotations": {"terms": {"field": "snp.annotations.impact"}}}})
    agg_annotation = A(
        {"nested": {"path": "snp.annotations"},
         "aggs": {"annotations": {"terms": {"field": "snp.annotations.effect"}}}})
    s.aggs.bucket('gene_count', agg_genes)
    s.aggs.bucket('snp_type_count', agg_snp_type)
    s.aggs.bucket('impact_count', agg_impact)
    s.aggs.bucket('annotation_count', agg_annotation)
    s.aggs.bucket('pvalue_hist', 'histogram', field='score', interval='1')
    s.aggs.bucket('maf_hist', 'histogram', field='maf', interval='0.1')
    agg_results = s.execute().aggregations
    results = {'gene_count': agg_results.gene_count.buckets, 'snp_type_count': agg_results.snp_type_count.buckets,
               'impact_count': agg_results.impact_count.annotations.buckets, 'annotation_count': agg_results.annotation_count.annotations.buckets,
               'pvalue_hist': agg_results.pvalue_hist.buckets, 'maf_hist': agg_results.maf_hist.buckets}
    return results

def load_genes_by_region(chrom, start, end, features):
    """Retrieve genes by region"""
    index = _get_index_from_chr(chrom)
    search_genes = Search().using(es).doc_type('genes').index(index).filter("range", positions={"lte": end, "gte":start})
    if not features:
        search_genes.source(exclude=['isoforms'])
    genes = [gene.to_dict() for gene in search_genes.scan() ]
    for gene in genes:
        gene['ko_associations'] = load_gene_ko_associations(gene['name'], return_only_significant=True)
    return genes


def filter_association_search(s, filters):
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
                    maf_filters.append(Q('range', maf={'lt':float(maf[0])/100}))
                else:
                    maf_filters.append(Q('range', maf={'gt':float(maf[0])/100}))
        s = s.filter(Q('bool',should = maf_filters))
    if 'mac' in filters and len(filters['mac']) == 1:
        if filters['mac'][0] == '0':
            s = s.filter('range', mac={'lte': 5})
        else:
            s = s.filter('range', mac={'gt': 5})
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
    if 'gene_id' in filters and len(filters['gene_id']) > 0:
        s = s.filter(Q({'nested': {'path': 'snp.annotations', 'query': {'match': {'snp.annotations.gene_name': filters['gene_id']}}}}) | (Q('range', snp__position={'gte': int(filters['start'])}) & Q('range', snp__position={'gte': int(filters['start'])})))
    if 'start' in filters:
        s = s.filter('range', snp__position={'gte': int(filters['start'])})
    if 'end' in filters:
        s = s.filter('range', snp__position={'lte': int(filters['end'])})
    if 'significant' in filters and len(filters['significant'])>0:
        if filters['significant'][0] == "b":
            s = s.filter('term', overBonferroni='T')
        elif filters['significant'][0] == "p":
            s = s.filter('term', overPermutation='T')
    return s

def get_aggregated_filtered_statistics(filters):
    s = Search(using=es, doc_type='associations')
    s = filter_association_search(s, filters)
    agg_chr = A("terms", field="snp.chr")
    agg_type = A("terms", field="snp.coding")
    agg_annotation = A(
        {"nested": {"path": "snp.annotations"}, "aggs": {"annotations": {"terms": {"field": "snp.annotations.effect"}}}})
    agg_maf = A("range", field="maf",
                ranges=[{"to": 0.01}, {"from": 0.01, "to": 0.05001}, {"from": 0.05001, "to": 0.1001}, {"from": 0.1001}])
    agg_mac = A("range", field="mac",
                ranges=[{"to": 6}, {"from": 6}])
    s.aggs.bucket('maf_count', agg_maf)
    s.aggs.bucket('mac_count', agg_mac)
    s.aggs.bucket('chr_count', agg_chr)
    s.aggs.bucket('type_count', agg_type)
    s.aggs.bucket('annotation_count', agg_annotation)
    agg_results = s.execute().aggregations
    return agg_results.chr_count.buckets, agg_results.maf_count.buckets, agg_results.mac_count.buckets, agg_results.type_count.buckets, agg_results.annotation_count.annotations.buckets

def index_associations(study, associations, thresholds):
    """indexes associations"""
    with_permutations = 'permutation_threshold' in thresholds.keys() and thresholds['permutation_threshold']
    thresholds_study = [{'name': key, 'value': val} for key, val in thresholds.items() ]
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
        study_data['thresholds'] = thresholds_study
        _source = {'mac': int(assoc['mac']), 'maf': float(assoc['maf']), 'score': float(assoc['score']), 'created': datetime.datetime.now(),'study':study_data, 'overFDR': bool(assoc['score'] > thresholds['bh_threshold'])}
        _source['overBonferroni'] = bool(assoc['score'] > thresholds['bonferroni_threshold05'])
        if with_permutations:
            _source['overPermutation'] = bool(assoc['score'] > thresholds['permutation_threshold'])
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
    s = filter_association_search(s, filters)
    s = s[start:start+size]
    print(json.dumps(s.to_dict()))
    result = s.execute()
    associations = result['hits']['hits']
    return [association['_source'].to_dict() for association in associations], result['hits']['total']

def load_filtered_top_associations_search_after(filters, search_after = ''):
    """Retrieves top associations and filter them through the tickable options"""
    s = Search(using=es, doc_type='associations')
    s = s.sort('-score', '_uid')
    s = filter_association_search(s, filters)
    if search_after != '':
        search_after = parse_lastel(search_after)
        print(search_after)
        s = s.extra(search_after=search_after)
    s = s[0:25]
    print(json.dumps(s.to_dict()))
    result = s.execute()
    associations = result['hits']['hits']
    last_el = ('','')
    if len(associations) > 0:
        last_el = result['hits']['hits'][-1]['sort']
    # Transformation needed to saveguard url transmition
        last_el[1] = "-".join(last_el[1].split('#'))
    return [association['_source'].to_dict() for association in associations], result['hits']['total'], last_el

def load_filtered_top_ko_associations_search_after(filters, search_after = '', size=50):
    """Retrieves top associations and filter them through the tickable options"""
    s = Search(using=es, doc_type='ko_associations')
    s = s.sort('-score', '_uid')
    # By default, leave out associations with no gene
    s = s.filter(Q({'nested':{'path':'gene', 'query':{'exists':{'field':'gene.chr'}}}}))

    # # Only need to filter by chromosome, maf or mac
    if 'chr' in filters and len(filters['chr']) > 0 and len(filters['chr']) < 5:
        s = s.filter(Q('bool', should=[Q({'nested':{'path':'gene', 'query':{'match':{'gene.chr':chrom if len(chrom) > 3 else 'chr%s' % chrom}}}}) for chrom in
                                       filters['chr']]))
    if 'significant' in filters:
        s = s.filter(Q('range', mac={'gte': 6}))
        s = s.filter('term', overBonferroni='T') # TODO: change this to permutation once the new indexed scores are in.
    if search_after != '':
        search_after = parse_lastel(search_after)
        print(search_after)
        s = s.extra(search_after=search_after)
    s = s[0:size]
    result = s.execute()
    associations = result['hits']['hits']
    last_el = result['hits']['hits'][-1]['sort']
    # Transformation needed to saveguard url transmition
    last_el[1] = "-".join(last_el[1].split('#'))
    return [association['_source'].to_dict() for association in associations], result['hits']['total'], last_el


def get_gwas_overview_bins_data(filters):
    """Collect the data used to plot the gwas heatmap histograms"""
    # Check missing filters
    filters = check_missing_filters(filters)
    # Params: chromosome (list or individual), region (optional, only considered if taking 1 chr), filters?
    region_bins = get_bins_for_chr_regions(filters)
    combined_data= []
    keys = list(region_bins)
    chromosome_sizes = {'chr1': 30427671, 'chr2': 19698289, 'chr3': 23459830,'chr4': 18585056, 'chr5': 26975502}
    keys.sort()
    for key in keys:
        if filters['region'][0] == '':
            region_final = [0, chromosome_sizes[key]]
        else:
            region_final = [filters['region'][0],filters['region'][1]]
        bin_sze = filters['region_width']
        combined_data.append({'chr': key, 'region':region_final, 'bin_sze': bin_sze, 'bins': region_bins[key]})
    # Get study list
    return {"type":"top", "data":combined_data}

def get_gwas_overview_heatmap_data(filters, num_studies):
    """Collect the data used to plot the gwas heatmap"""
    # Check missing filters
    filters = check_missing_filters(filters)
    # Params: chromosome (list or individual), region (optional, only considered if taking 1 chr), filters?
    max_score = dict()
    data = dict()
    if filters['chrom']=='all':
        for i in range(1,6):
            chr = 'chr' + str(i)
            filters['chrom'] = chr
            max_score_temp, data_temp = get_top_hits_for_all_studies(filters, num_studies) # TODO: link parameters from rest endpoint
            max_score[chr]=max_score_temp[chr]
            data[chr] = data_temp[chr]
        # Aggregate over chromosomes
        combined_data = combine_data(max_score, data) # For testing: change to data_bis to get faster but more localized points (looks bad)
    else:
        chr = 'chr'+str(filters['chrom'][-1])
        max_score_temp, data_temp = get_top_hits_for_all_studies(filters, num_studies)  # TODO: link parameters from rest endpoint
        max_score[chr] = max_score_temp[chr]
        data[chr] = data_temp[chr]
        combined_data = combine_data(max_score, data, region=filters['region'],region_width=filters['region_width'])
    # Get study list
    return {"type":"top", "scoreRange": [0, max(max_score.values())], "data":combined_data}

def check_missing_filters(filters):
    if 'chrom' not in filters.keys():
        filters['chrom'] = 'all'
    if 'region_width' not in filters.keys():
        filters['region_width'] = 250000
    if 'threshold' not in filters.keys():
        filters['threshold'] = ''
    if 'region' not in filters.keys():
        filters['region'] = ('','')
    if 'maf' not in filters.keys():
        filters['maf'] = 0
    if 'mac' not in filters.keys():
        filters['mac'] = 6
    return filters

def get_top_hits_for_all_studies(filters, num_studies):
    s = Search(using=es, doc_type='associations')
    s = filter_heatmap_search(s, filters)
    # First aggregate for studies
    s.aggs.bucket('per_chrom', 'terms', field='snp.chr')
    # Keep track of the maximum value for each study
    s.aggs['per_chrom'].metric('max', 'max', field='score')
    # Then aggregate for chromosomes
    s.aggs['per_chrom'].bucket('per_study', 'terms', field='study.id', order={'_term':'asc'}, size=num_studies,min_doc_count='0') #TODO: automatically check number of studies
    s.aggs['per_chrom']['per_study'].metric('top_N', 'top_hits', size='25', sort={'score':'desc'}, _source=['-score','snp.position'])
    # Then for regions (to avoid too many overlapping hits)
    s.aggs['per_chrom']['per_study'].bucket('per_region', 'histogram', field='snp.position', interval=str(filters['region_width']))
    # Then state what info we want from top_hits (position and score)
    s.aggs['per_chrom']['per_study']['per_region'].metric('top', 'top_hits', size='1', sort={'score':'desc'}, _source=['score','snp.position'])
    # Aggregate results
    agg_results = s.execute().aggregations
    # Find max score for
    max_score = dict()
    data = dict()
    data_bis = dict()
    for bucket in agg_results.per_chrom.buckets:
        max_score[bucket.key] = bucket.max.value
        data[bucket.key] = []
        # data_bis[bucket.key] = []
        for element in bucket.per_study.buckets:
            # Combine results and get top 25 per chrom per study:
            data[bucket.key].append(get_top_N_per_study(element, 25))
            # study_data = []
            # for top in element.top_N.hits.hits:
            #     study_data.append({'pos': top['_source']['snp']['position'],
            #                                  'score': top['_source']['score']})
            # data_bis[bucket.key].append(study_data)
    return max_score, data #, data_bis

def get_top_N_per_study(bucket, N=25):
    hits = []
    for element in bucket.per_region.buckets:
        if element.top.hits.hits:
            hits.append({'pos': element.top.hits.hits[0]['_source']['snp']['position'],'score':element.top.hits.hits[0]['_source']['score']})
    hits.sort(key=lambda tup: -tup['score'])
    return hits[:N]


def filter_heatmap_search(s, filters):
    if filters['chrom'] != 'all':
        s = s.filter(Q('bool', should=[Q('term', snp__chr=filters['chrom'] if len(filters['chrom']) > 3 else 'chr%s' % filters['chrom'])]))
    if filters['threshold'] == 'FDR':
        s = s.filter('term', overFDR='T')
    elif filters['threshold'] == 'Bonferroni':
        s = s.filter('term', overBonferroni='T')
    elif filters['threshold'] == 'permutation':
        s = s.filter('term', overPermutation='T')
    if filters['maf'] > 0:
        s = s.filter(Q('range', maf={'gte':filters['maf']}))
    if filters['mac'] > 0:
        s = s.filter(Q('range', mac={'gte': filters['mac']}))
    if filters['region'][0] != '':
        s = s.filter('range', snp__position={'gte': int(filters['region'][0])})
        s = s.filter('range', snp__position={'lte': int(filters['region'][1])})
    return s

def get_bins_for_chr_regions(filters):
    """Usage:
        chrom = indicate the chromosome(s) of interest ('all' or any chromosome),
        region_width = indicate the size of the bins for which to count hits,
        threshold = indicate the type of threshold to look at (FDR, Bonferroni, permutation or none)
        region = indicate a specific window in which to aggregate for, default = ('','') looks at entire chromosome
        maf = indicate a minimum maf
        mac = indicate a minimum mac
    """
    s = Search(using=es, doc_type='associations')
    s = filter_heatmap_search(s, filters)
    s.aggs.bucket('per_chrom', 'terms', field='snp.chr').bucket('per_region', 'histogram', field='snp.position', interval=str(filters['region_width']))
    agg_results = s.execute().aggregations
    bin_dict = dict()
    for buckets in agg_results.per_chrom.buckets:
        bin_dict[buckets['key']] = convert_to_bin_format(buckets['per_region'].buckets)
    return bin_dict

def convert_to_bin_format(buckets):
    bins = []
    for bin in buckets:
        bins.append(bin['doc_count'])
    return bins

def combine_data(max_scores, data, region=('',''), region_width=10000):
    if len(data) != len(max_scores):
        raise ValueError('Problem with the size of the dictionaries')
    final_data = []
    keys = list(data)
    chromosome_sizes = {'chr1': 30427671, 'chr2': 19698289, 'chr3': 23459830,'chr4': 18585056, 'chr5': 26975502}
    keys.sort()
    for key in keys:
        scoreRange = [0,max_scores[key]]
        if region[0] == '':
            region_final = [0, chromosome_sizes[key]]
        else:
            region_final = [region[0],region[1]]
        bin_sze = region_width
        final_data.append({'scoreRange': scoreRange, 'chr': key, 'region':region_final, 'bin_sze': bin_sze,
                           'data':data[key]})
    return final_data


def index_genes(genes):
    """Indexes the genes"""
    num_genes = len(genes)
    documents = [{'_index':'geno_%s' % gene['chr'].lower(),'_type':'genes','_id':gene_id,'_source':gene} for gene_id, gene in genes.items()]
    success, errors = helpers.bulk(es,documents,chunk_size=10000,stats_only=True,request_timeout=300)
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

def _get_index_from_chr(chrom):
    index = 'geno_%s'
    if len(chrom) > 3:
        index = index % chrom
    else:
        index = index % 'chr' + chrom
    return index

# Need to index KO genes association differently.

def index_ko_associations(study, associations, thresholds):
    """
    indexes gene knockout associations

    They are stored differently cause they represent associations between genes and phenotypes
    """
    with_permutations = 'permutation_threshold' in thresholds.keys() and thresholds['permutation_threshold'] # This will always be FALSE
    thresholds_study = [{'name': key, 'value': val} for key, val in thresholds.items() ]
    annotations = {}
    documents = []
    for assoc in associations:
        _id = '%s_%s' % (study.pk, assoc['gene'])
        study_data = serializers.EsStudySerializer(study).data
        study_data['thresholds'] = thresholds_study
        _source = {'mac': int(assoc['mac']), 'maf': float(assoc['maf']), 'score': float(assoc['score']), 'beta': float(assoc['beta']),
            'se_beta': float(assoc['se_beta']), 'created': datetime.datetime.now(),'study':study_data}
        _source['overBonferroni'] = bool(assoc['score'] > thresholds['bonferroni_threshold05'])
        if with_permutations:
            _source['overPermutation'] = bool(assoc['score'] > thresholds['permutation_threshold'])
        try:
            gene = load_gene_by_id(assoc['gene'])
        except:
            gene = {'name': assoc['gene']}
        _source['gene'] = gene
        documents.append({'_index':'aragwas','_type':'ko_associations','_id': _id, '_source': _source })
    if len(documents) == 0:
        return 0,0
    success, errors = helpers.bulk(es,documents, chunk_size=1000, stats_only=True)
    return success, errors

def load_gene_ko_associations(id, return_only_significant=False):
    """Retrieve KO associations by gene id"""
    matches = GENE_ID_PATTERN.match(id)
    if not matches:
        raise Exception('Wrong Gene ID %s' % id)
    chrom = matches.group(1)
    asso_search = Search(using=es).doc_type('ko_associations')
    if return_only_significant:
        asso_search = asso_search.filter('term', overBonferroni='T')
#     q = Q('bool', should=Q('term',gene__name = id))
    q = Q({'nested':{'path':'gene', 'query':{'match':{'gene.name':id}}}})
    asso_search = asso_search.filter(q).sort('-score').source(exclude=['gene'])
    results = asso_search[0:min(500, asso_search.count())].execute()
    ko_associations = results.to_dict()['hits']['hits']
    return [association['_source'] for association in ko_associations]
