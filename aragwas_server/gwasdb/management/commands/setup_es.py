from django.core.management.base import BaseCommand, CommandError
import argparse
from gwasdb.parsers import parse_genes
from gwasdb import elastic
import traceback

class Command(BaseCommand):
    help = 'setup es elasticsearch db'

    def add_arguments(self, parser):
        parser.add_argument('gff3_file',
                            help='Specify the GFF3 file for the genes')
        parser.add_argument('go_terms_file',
                            help='Specify file with the gene ontology terms')
        parser.add_argument('snpeff_file',
                            help='Specify snpeff file for the snps')

    def handle(self, *args, **options):
        try:
            # check if ES index exists and push templates.
            elastic.check_indices()
            genes = parse_genes(options['gff3_file'], options['go_terms_file'])
            self.stdout.write('Indexing genes...')
            indexed_genes, failed_genes = elastic.index_genes(genes)
            if failed_genes == 0:
                self.stdout.write(self.style.SUCCESS(
                'Successfully indexed all %s genes in elasticsearch' % len(genes)))
            else:
                self.stdout.write(self.style.WARNING(
                '%s/%s genes failed to index in elasticsearch' % (len(failed_genes), len(genes))))
            self.stdout.write('Indexing SNPs...')
            indexed_snps, failed_snps = elastic.index_snps(options['snpeff_file'])
            if failed_snps == 0:
                self.stdout.write(self.style.SUCCESS(
                'Successfully indexed all %s SNPs in elasticsearch' % indexed_snps))
            else:
                self.stdout.write(self.style.WARNING(
                '%s/%s SNPs failed to index in elasticsearch' % (failed_snps, indexed_snps + failed_snps)))
        except Exception as err:
            traceback.print_exc()
            raise CommandError(
                'Error initializing elasticsearch database Reason: %s' % str(err))

        self.stdout.write(self.style.SUCCESS(
            'Successfully initialiazed elasticseach database'))
