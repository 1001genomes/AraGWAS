from django.core.management.base import BaseCommand, CommandError
from gwasdb.hdf5 import get_hit_count, load_permutation_thresholds
from gwasdb.models import Study, Phenotype, Genotype
from aragwas import settings
import os, requests, shutil


class Command(BaseCommand):
    help = 'Get an HDF5 file of a newly computed GWAS and create an entry in the study model with all relevant information'

    def add_arguments(self, parser):
        parser.add_argument('--hdf5',
                            dest='hdf5_file',
                            type=int,
                            default=None,
                            help='Specify the name of the new hdf5 file.')
        parser.add_argument('--phenotype_id',
                            dest='phenotype_id',
                            type=int,
                            default=None,
                            help='Specify the id of the related phenotype.')
        parser.add_argument('--genotype_id',
                            dest='genotype_id',
                            type=int,
                            default=None,
                            help='Specify the id of the related genotype.')
        parser.add_argument('--method',
                            dest='method',
                            type=int,
                            default=None,
                            help='Specify the method used in the GWAS.')
        parser.add_argument('--transformation',
                            dest='transformation',
                            type=int,
                            default=None,
                            help='Specify the phenotype transformation used before the GWAS.')
        parser.add_argument('--permutation',
                            dest='permutation',
                            type=float,
                            default=None,
                            help='Specify the permutation threshold of the new study.')
        parser.add_argument('--publication',
                            dest='publication',
                            type=str,
                            default=None,
                            help='Specify the name of the publication.')
        parser.add_argument('--pmid',
                            dest='permutation_pmid',
                            type=float,
                            default=None,
                            help='Specify the pubmed id of the original publication.')

    def handle(self, *args, **options):
        hdf5_file = options.get('hdf5_file', None)
        phenotype_id = options.get('phenotype_id', None)
        genotype_id = options.get('genotype_id', None)
        method = options.get('method', None)
        transformation = options.get('transformation', None)
        perm_threshold = options.get('permutation', None)
        pmid = options.get('publication_pmid', None)
        publication = options.get('publication', None)
        try:
            if hdf5_file:
                id = hdf5_file.split(".")[0]
                if not os.path.isfile(hdf5_file):
                    raise ValueError("The provided file name does not match any file. (--hdf5)")
            else:
                raise ValueError("You must provide a valid hdf5 file path. (--hdf5)")
            # checks
            if None in [phenotype_id, genotype_id, method, transformation]:
                raise ValueError("You must provide phenotype_id, genotype_id, method and transformation")

            if not perm_threshold:
                print("WARNING: NO PERMUTATION THRESHOLD PROVIDED. You will need to update the study once you have a permutation value.")
            try:
                # Get phenotype information
                try:
                    phenotype = Phenotype.objects.get(pk=phenotype_id)
                except Exception as err:
                    raise CommandError('Impossible to find phenotype, did you import it? (reason: %s)' %str(err))
                # Get genotype information
                try:
                    genotype = Genotype.objects.get(pk=genotype_id)
                except Exception as err:
                    raise CommandError('Impossible to find genotype? (reason: %s)' %str(err))

                # Get n_hits
                hits, thresholds = get_hit_count(hdf5_file, maf=0.05, perm_threshold=perm_threshold)
                # Get n_samples
                r = requests.get(
                    'https://arapheno.1001genomes.org/rest/phenotype/' + str(phenotype_id) + '/values.json')
                accessions = r.json()
                countries = [acc['accession_country'] for acc in accessions]

                study = Study(
                    name=phenotype["name"]+"_"+transformation+"_"+genotype["name"]+"_"+method,
                    transformation=transformation,
                    genotype=genotype,
                    phenotype=phenotype,
                    method=method,
                    n_hits_bonf=hits['bonferroni_hits05'],
                    n_hits_thr=hits['thr_e-4'],
                    n_hits_fdr=hits['bh_hits'],
                    bonferroni_threshold=thresholds['bonferroni_threshold05'],
                    bh_threshold=thresholds['bh_threshold'],
                    n_hits_total=thresholds['total_associations'],
                    number_samples=len(accessions),
                    number_countries=len(set(countries)),
                )


                if perm_threshold:
                    study.n_hits_perm = hits['permutation_hits']
                    study.permutation_threshold = thresholds['permutation']
                if publication:
                    study.publication_name = publication
                if pmid:
                    study.publication_pmid = pmid
                study.save()
                # copy file
                print("Copying file to AraGWAS folder...")
                hdf5_ag_file = os.path.join(settings.HDF5_FILE_PATH, 'gwas_results', '%s.hdf5' % study.pk)
                if hdf5_file != hdf5_ag_file:
                    shutil.copyfile(hdf5_file, hdf5_ag_file)
                    print("Done")
                else:
                    print("File is already on the regular AraGWAS config")
            except Exception as err:
                self.stdout.write(self.style.ERROR('Impossible to save study from file. Reason:' % str(err)))
        except Exception as err:
            raise CommandError(
                'Error saving phenotypes. Reason: %s' % str(err))

# # Publication dict for available studies...
# publication_links_dict = {
#                 'Atwell et. al, Nature 2010': 'https://doi.org/10.1038/nature08800',
#                 'Flowering time in simulated seasons': 'https://doi.org/10.1073/pnas.1007431107',
#                 'Mejion': 'https://doi.org/10.1038/ng.2824',
#                 'DAAR': 'https://doi.org/10.1073/pnas.1503272112',
#                 'Ion Concentration':'https://doi.org/10.1371/journal.pbio.1002009',
#                 '1001genomes flowering time phenotypes': 'https://doi.org/10.1016/j.cell.2016.05.063'}
# publication_PMID = {
#     'Atwell et. al, Nature 2010': '20336072',
#     'Flowering time in simulated seasons': '21078970',
#     'Mejion': '24212884',
#     'DAAR': '26324904',
#     'Ion Concentration': '25464340',
#     '1001genomes flowering time phenotypes': '27293186'
# }
# publication_PMCID = {
#     'Atwell et. al, Nature 2010': 'PMC3023908',
#     'Flowering time in simulated seasons': 'PMC3000268',
#     'Mejion': '',
#     'DAAR': 'PMC4577208',
#     'Ion Concentration': 'PMC4251824',
#     '1001genomes flowering time phenotypes': 'PMC4949382'
# }