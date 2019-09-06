from django.core.management.base import BaseCommand, CommandError
from gwasdb.models import Phenotype
import requests


class Command(BaseCommand):
    help = 'Index AraPheno phenotypes in AraGWASCatalog'

    def add_arguments(self, parser):
        parser.add_argument('--id',
                            dest='phenotype_id',
                            type=int,
                            default=None,
                            help='Specify a primary key to index a specific phenotype. If empty will check entire phenotype list.')
        parser.add_argument('--update',
                            dest='update',
                            type=bool,
                            default=False,
                            help='Update existing phenotypes.')

    def handle(self, *args, **options):
        phenotype_id = options.get('phenotype_id', None)
        update = options.get('update', False)
        try:
            if phenotype_id:
                r = requests.get('https://arapheno.1001genomes.org/rest/phenotype/list.json')
                phenos_arapheno = [r.json()]
            else:
                # Retrieve list of all phenotypes from AraPheno:
                r = requests.get('https://arapheno.1001genomes.org/rest/phenotype/list.json')
                phenos_arapheno = r.json()
            # check if phenotypes are stored in AraGWASCatalog
            ids_aragwas = Phenotype.objects.all().values_list('id', flat=True)
            counter = 0
            for pheno in phenos_arapheno:
                if pheno['phenotype_id'] not in ids_aragwas or update:
                    # Add to table:
                    p = Phenotype(pk=pheno['phenotype_id'], name=pheno['name'], study_name=pheno['study'], description=pheno['scoring'], date=pheno['integration_date'], arapheno_link="https://arapheno.1001genomes.org/phenotype/"+str(pheno['phenotype_id']), trait_ontology_id=pheno['to_term'] if pheno['to_term'] is not None else "", trait_ontology_name=pheno['to_name'] if pheno['to_name'] is not None else "", trait_ontology_description=pheno['to_definition'])
                    p.save()
                    counter += 1
                # else:
                    # # add ontology information (this line will be removed after one call...
                    # p = Phenotype.objects.get(pk=pheno['phenotype_id'])
                    # p.trait_ontology_id = pheno['to_term'] if pheno['to_term'] is not None else ""
                    # p.trait_ontology_name = pheno['to_name'] if pheno['to_name'] is not None else ""
                    # p.trait_ontology_description=pheno['to_definition']
                    # p.save()
                    # counter += 1
            print(str(counter) + ' new phenotype(s) added to the database.')
        except Exception as err:
            raise CommandError(
                'Error saving phenotypes. Reason: %s' % str(err))