from django.core.management.base import BaseCommand, CommandError
from gwasdb.models import Study
import requests


class Command(BaseCommand):
    help = 'Index AraPheno phenotypes in AraGWASCatalog'

    def handle(self, *args, **options):
        try:
            publication_links_dict = {'Atwell et. al, Nature 2010': 'https://doi.org/10.1038/nature08800', 'Flowering time in simulated seasons': 'https://doi.org/10.1073/pnas.1007431107', 'Mejion': 'https://doi.org/10.1038/ng.2824', 'DAAR': 'https://doi.org/10.21958/STUDY:4', 'Ion Concentration':'https://doi.org/10.21958/STUDY:16', '1001genomes flowering time phenotypes': 'https://doi.org/10.21958/STUDY:12'}
            # Retrieve list of all phenotypes from AraPheno:
            r = requests.get('https://arapheno.1001genomes.org/rest/phenotype/list.json')
            phenos_arapheno = r.json()
            # check if phenotypes are stored in AraGWASCatalog
            ids_aragwas = Study.objects.all().values_list('id', flat=True)
            counter = 0
            for pheno in phenos_arapheno:
                if pheno['phenotype_id'] in ids_aragwas:
                    # Add to table:
                    p = Study.objects.get(pk=pheno['phenotype_id'])
                    p.publication = publication_links_dict[pheno['study']]
                    p.save()
                    counter += 1
            print(str(counter) + ' new publication(s) added to the database.')
        except Exception as err:
            raise CommandError(
                'Error saving studies. Reason: %s' % str(err))