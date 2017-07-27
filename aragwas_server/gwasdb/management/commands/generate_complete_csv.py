from django.core.management.base import BaseCommand, CommandError
import argparse
from gwasdb.parsers import parse_genes
from gwasdb import elastic
import traceback
from gwasdb import es2csv

class Command(BaseCommand):
    help = 'Generate overall csv file for one doc type (associations, genes or snps) to make available for direct download.'

    def add_arguments(self, parser):
        parser.add_argument('doc_type',
                            help='Specify the doc type for which you would like to generate the csv file')

    def handle(self, *args, **options):
        try:
            # Generate the necessary opts and filters
            elastic.check_indices()
            opts = dict()
            opts['doc_type'] = options['doc_type']
            self.stdout.write('Generating file for {}...'.format(opts['doc_type']))
            opts['output_file'] = opts['doc_type'] + "_all.csv"

            # Generate file through es2csv
            es2csv.prepare_csv(opts=opts,filters=dict())


        except Exception as err:
            traceback.print_exc()
            raise CommandError(
                'Error generating csv file. Reason: %s' % str(err))

        self.stdout.write(self.style.SUCCESS(
            'Successfully initialiazed elasticseach database'))

    def prepare_csv(opts, filters):
        """Usage:
            p.add_argument('-i', '--index-prefixes', dest='index_prefixes', default=['logstash-*'], type=str, nargs='+', metavar='INDEX', help='Index name prefix(es). Default is %(default)s.')
            p.add_argument('-D', '--doc_types', dest='doc_type', type=str, nargs='+', metavar='DOC_TYPE', help='Document type.')
            p.add_argument('-t', '--tags', dest='tags', type=str, nargs='+', help='Query tags.')
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