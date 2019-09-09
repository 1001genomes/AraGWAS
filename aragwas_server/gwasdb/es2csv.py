#!/usr/bin/env python
"""
copyright: Apache License 2.0, adapted from: https://github.com/taraslayshchuk/es2csv
original title:           A CLI tool for exporting data from Elasticsearch into a CSV file.
original description:     Command line utility, written in Python, for querying Elasticsearch in Lucene query syntax or Query DSL syntax and exporting result as documents into a CSV file.
original usage:           es2csv -q '*' -i _all -e -o ~/file.csv -k -m 100
                 es2csv -q '{"query": {"match_all": {}}}' -r -i _all -o ~/file.csv
                 es2csv -q @'~/long_query_file.json' -r -i _all -o ~/file.csv
                 es2csv -q '*' -i logstash-2015-01-* -f host status message -o ~/file.csv
                 es2csv -q 'host: localhost' -i logstash-2015-01-01 logstash-2015-01-02 -f host status message -o ~/file.csv
                 es2csv -q 'host: localhost AND status: GET' -u http://kibana.com:80/es/ -o ~/file.csv
                 es2csv -q '*' -t dev prod -u http://login:password@kibana.com:6666/es/ -o ~/file.csv
                 es2csv -q '{"query": {"match_all": {}}, "filter":{"term": {"tags": "dev"}}}' -r -u http://login:password@kibana.com:6666/es/ -o ~/file.csv

"""
import os
import sys
import time
import argparse
import json
import csv
import zipfile
import elasticsearch
from functools import wraps
from aragwas.settings import ES_HOST, HDF5_FILE_PATH

from gwasdb.elastic import filter_association_search
from elasticsearch_dsl import Search

FLUSH_BUFFER = 1000  # Chunk of docs to flush in temp file
TIMES_TO_TRY = 3
RETRY_DELAY = 60
META_FIELDS = ['_id', '_index', '_score', '_type']


# Retry decorator for functions with exceptions
def retry(ExceptionToCheck, tries=TIMES_TO_TRY, delay=RETRY_DELAY):
    def deco_retry(f):
        @wraps(f)
        def f_retry(*args, **kwargs):
            mtries = tries
            while mtries > 0:
                try:
                    return f(*args, **kwargs)
                except ExceptionToCheck as e:
                    print(e)
                    print('Retrying in %d seconds ...' % delay)
                    time.sleep(delay)
                    mtries -= 1
            try:
                return f(*args, **kwargs)
            except ExceptionToCheck as e:
                print('Fatal Error: %s' % e)
                exit(1)

        return f_retry

    return deco_retry


class Es2csv:

    def __init__(self, opts, filters):
        self.opts = opts
        self.filters = filters

        self.num_results = 0
        self.scroll_ids = []
        self.scroll_time = '30m'

        self.csv_headers = list(META_FIELDS) if self.opts['meta_fields'] else []
        self.tmp_file = '%s.tmp' % opts['output_file']

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def create_connection(self):
        es = elasticsearch.Elasticsearch([ES_HOST],timeout=60)
        self.es_conn = es

    @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
    def search_query(self):
        print(self.opts)
        @retry(elasticsearch.exceptions.ConnectionError, tries=TIMES_TO_TRY)
        def next_scroll(scroll_id):
            return self.es_conn.scroll(scroll=self.scroll_time, scroll_id=scroll_id)
        search_args = dict(
            doc_type=self.opts['doc_type'],
            scroll=self.scroll_time,
            size=self.opts['scroll_size'],
            terminate_after=self.opts['max_results']
        )

        ### Alternative search with elastic.py functions
        s = Search(using=self.es_conn, doc_type=self.opts['doc_type'])
        if self.opts['doc_type']=='associations':
            s = s.sort('-score')
            s = filter_association_search(s, self.filters)
        else:
            s = s.sort('name')
        # Transform the query into a json object
        query = str(s.to_dict()).replace("'",'"')
        try:
            query = json.loads(query)
        except ValueError as e:
            print('Invalid JSON syntax in query. %s' % e)
            exit(1)
        search_args['body'] = query
        print(query)

        if '_all' not in self.opts['fields']:
            search_args['_source_include'] = ','.join(self.opts['fields'])
            self.csv_headers.extend([field for field in self.opts['fields'] if '*' not in field])

        if self.opts['debug_mode']:
            print('Query[%s]: %s' % (('Query DSL', json.dumps(query))))
            print('Output field(s): %s' % ', '.join(self.opts['fields']))

        res = self.es_conn.search(**search_args)

        self.num_results = res['hits']['total']

        if self.opts['debug_mode']:
            print('Found %s results' % self.num_results)
            print(json.dumps(res))

        if self.num_results > 0:
            open(self.opts['output_file'], 'w').close()
            open(self.tmp_file, 'w').close()

            hit_list = []
            total_lines = 0

            while total_lines != self.num_results:
                if res['_scroll_id'] not in self.scroll_ids:
                    self.scroll_ids.append(res['_scroll_id'])

                if not res['hits']['hits']:
                    print('Scroll[%s] expired(multiple reads?). Saving loaded data.' % res['_scroll_id'])
                    break
                for hit in res['hits']['hits']:
                    total_lines += 1
                    hit_list.append(hit)
                    if len(hit_list) == FLUSH_BUFFER:
                        self.flush_to_file(hit_list)
                        hit_list = []
                    if self.opts['max_results']:
                        if total_lines == self.opts['max_results']:
                            self.flush_to_file(hit_list)
                            print('Hit max result limit: %s records' % self.opts['max_results'])
                            return
                res = next_scroll(res['_scroll_id'])
            self.flush_to_file(hit_list)

    def flush_to_file(self, hit_list):
        def to_keyvalue_pairs(source, ancestors=[], header_delimeter='.'):
            def is_list(arg):
                return type(arg) is list

            def is_dict(arg):
                return type(arg) is dict

            if is_dict(source):
                for key in source.keys():
                    to_keyvalue_pairs(source[key], ancestors + [key])

            elif is_list(source):
                if self.opts['kibana_nested']:
                    [to_keyvalue_pairs(item, ancestors) for item in source]
                else:
                    [to_keyvalue_pairs(item, ancestors + [str(index)]) for index, item in enumerate(source)]
            else:
                header = header_delimeter.join(ancestors)
                if header not in self.csv_headers:
                    self.csv_headers.append(header)
                try:
                    out[header] = '%s%s%s' % (out[header], self.opts['delimiter'], source)
                except:
                    out[header] = source

        with open(self.tmp_file, 'a') as tmp_file:
            for hit in hit_list:
                out = {field: hit[field] for field in META_FIELDS} if self.opts['meta_fields'] else {}
                if '_source' in hit and len(hit['_source']) > 0:
                    to_keyvalue_pairs(hit['_source'])
                    tmp_file.write('%s\n' % json.dumps(out))
        tmp_file.close()

    def write_to_csv(self):
        if self.num_results > 0:
            self.num_results = sum(1 for line in open(self.tmp_file, 'r'))
            if self.num_results > 0:
                output_file = open(self.opts['output_file'], 'w+')
                csv_writer = csv.DictWriter(output_file, fieldnames=self.csv_headers, delimiter=self.opts['delimiter'])
                csv_writer.writeheader()

                for line in open(self.tmp_file, 'r'):
                    line_as_dict = json.loads(line)
                    line_dict_utf8 = {k: v for k, v in line_as_dict.items()}
                    csv_writer.writerow(line_dict_utf8)
                output_file.close()
            else:
                print('There is no docs with selected field(s): %s.' % ','.join(self.opts['fields']))
            os.remove(self.tmp_file)

    def clean_scroll_ids(self):
        try:
            self.es_conn.clear_scroll(body=','.join(self.scroll_ids))
        except:
            pass

def add_default_options(opts):
    if 'fields' not in opts.keys():
        # Default included fields
        if opts['doc_type'] == 'associations':
            opts['fields'] = ['snp.chr','snp.position', 'score', 'maf', 'mac', 'study.name', 'study.id',
                              'study.phenotype.name', 'study.genotype.name', 'study.thresholds', 'overFDR',
                              'overBonferroni', 'overPermutation','snp.ref', 'snp.alt', 'snp.coding', 'snp.gene_name',
                              'snp.annotations']
        else:
            opts['fields'] = ['_all']
    if 'delimiter' not in opts.keys():
        opts['delimiter'] = ','
    if 'max_results' not in opts.keys():
        opts['max_results'] = 0
    if 'scroll_size' not in opts.keys():
        opts['scroll_size'] = 1000
    if 'kibana_nested' not in opts.keys():
        opts['kibana_nested'] = False
    if 'meta_fields' not in opts.keys():
        opts['meta_fields'] = False
    if 'debug_mode' not in opts.keys():
        opts['debug_mode'] = False

    return opts


def prepare_csv(opts, filters):
    """Usage:
        p.add_argument('-i', '--index-prefixes', dest='index_prefixes', default=['logstash-*'], type=str, nargs='+', metavar='INDEX', help='Index name prefix(es). Default is %(default)s.')
        p.add_argument('-D', '--doc_type', dest='doc_type', type=str, nargs='+', metavar='DOC_TYPE', help='Document type.')
        p.add_argument('-o', '--output_file', dest='output_file', type=str, required=True, metavar='FILE', help='CSV file location.')
        p.add_argument('-f', '--fields', dest='fields', default=['_all'], type=str, nargs='+', help='List of selected fields in output. Default is %(default)s.')
        p.add_argument('-d', '--delimiter', dest='delimiter', default=',', type=str, help='Delimiter to use in CSV file. Default is "%(default)s".')
        p.add_argument('-m', '--max', dest='max_results', default=0, type=int, metavar='INTEGER', help='Maximum number of results to return. Default is %(default)s.')
        p.add_argument('-s', '--scroll_size', dest='scroll_size', default=100, type=int, metavar='INTEGER', help='Scroll size for each batch of results. Default is %(default)s.')
        p.add_argument('-k', '--kibana_nested', dest='kibana_nested', action='store_true', help='Format nested fields in Kibana style.')
        p.add_argument('-r', '--raw_query', dest='raw_query', action='store_true', help='Switch query format in the Query DSL.')
        p.add_argument('-e', '--meta_fields', dest='meta_fields', action='store_true', help='Add meta-fields in output.')
        p.add_argument('--debug', dest='debug_mode', action='store_true', help='Debug mode on.')
    """

    # opts = p.parse_args()
    # Check for missing options
    opts = add_default_options(opts)

    es = Es2csv(opts, filters)
    es.create_connection()
    es.search_query()
    es.write_to_csv()
    es.clean_scroll_ids()

def generate_all_associations_file():
    csv_filename = os.path.join(HDF5_FILE_PATH, 'all_associations.csv' )
    opts=dict(output_file=csv_filename, doc_type='associations')
    prepare_csv(opts, dict())
    with zipfile.ZipFile(os.path.join(HDF5_FILE_PATH, "all_associations.zip" ), 'w') as myzip:
        myzip.write(csv_filename)
        os.remove(csv_filename)