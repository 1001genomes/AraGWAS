from django.core.management.base import BaseCommand, CommandError
from gwasdb.models import Study
import requests


class Command(BaseCommand):
    help = 'Index AraPheno phenotypes in AraGWASCatalog'

    def handle(self, *args, **options):
        try:
            publication_links_dict = {
                'Atwell et. al, Nature 2010': 'https://doi.org/10.1038/nature08800',
                'Flowering time in simulated seasons': 'https://doi.org/10.1073/pnas.1007431107',
                'Mejion': 'https://doi.org/10.1038/ng.2824',
                'DAAR': 'https://doi.org/10.1073/pnas.1503272112',
                'Ion Concentration':'https://doi.org/10.1371/journal.pbio.1002009',
                '1001genomes flowering time phenotypes': 'https://doi.org/10.1016/j.cell.2016.05.063'}
            publication_PMID = {
                'Atwell et. al, Nature 2010': '20336072',
                'Flowering time in simulated seasons': '21078970',
                'Mejion': '24212884',
                'DAAR': '26324904',
                'Ion Concentration': '25464340',
                '1001genomes flowering time phenotypes': '27293186'
            }
            publication_PMCID = {
                'Atwell et. al, Nature 2010': 'PMC3023908',
                'Flowering time in simulated seasons': 'PMC3000268',
                'Mejion': '',
                'DAAR': 'PMC4577208',
                'Ion Concentration': 'PMC4251824',
                '1001genomes flowering time phenotypes': 'PMC4949382'
            }
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
                    p.publication_name = pheno['study']
                    p.publication = publication_links_dict[pheno['study']]
                    p.publication_pmid = publication_PMID[pheno['study']]
                    p.publication_pmcid = publication_PMCID[pheno['study']]
                    p.save()
                    counter += 1
            print(str(counter) + ' new publication(s) added to the database.')
        except Exception as err:
            raise CommandError(
                'Error saving studies. Reason: %s' % str(err))