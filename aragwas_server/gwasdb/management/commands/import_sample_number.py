from django.core.management.base import BaseCommand, CommandError
from gwasdb.models import Study
import requests


class Command(BaseCommand):
    help = 'Import AraPheno phenotypes number of accession in AraGWASCatalog Study model'

    def add_arguments(self, parser):
        parser.add_argument('--id',
                            dest='phenotype_id',
                            type=int,
                            default=None,
                            help='Specify a primary key to index a specific phenotype. If empty will check entire phenotype list.')

    def handle(self, *args, **options):
        phenotype_id = options.get('phenotype_id', None)
        try:
            if phenotype_id:
                ids_aragwas = [phenotype_id]
            else:
                # Retrieve list of all studies in AraGWAS:
                ids_aragwas = Study.objects.all().values_list('id', flat=True)
            # load phenotypes accession from AraPheno
            counter = 0
            for id in ids_aragwas:
                study = Study.objects.get(pk=id)
                if study.number_samples == None:
                    r = requests.get('https://arapheno.1001genomes.org:443/rest/phenotype/' + str(id) + '/values.json')
                    accessions = r.json()
                    countries = [acc['accession_country'] for acc in accessions]
                    study.number_samples = len(accessions)
                    study.number_countries = len(set(countries))
                    study.save()
                    counter +=1
            print(str(counter) + ' studies updated in the database.')
        except Exception as err:
            raise CommandError(
                'Error saving phenotypes. Reason: %s' % str(err))