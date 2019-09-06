from django.core.management.base import BaseCommand, CommandError
from gwasdb.hdf5 import get_hit_count, load_permutation_thresholds
from gwasdb.models import Study, Phenotype, Genotype
from aragwas import settings
from gwasdb.hdf5 import load_permutation_thresholds
import os, requests, shutil
import math


class Command(BaseCommand):
    help = 'Update existing GWAS studies from a folder with HDF5 files'

    def add_arguments(self, parser):
        parser.add_argument('hdf5_folder',
                            help='Folder with all HDF5 files')

        parser.add_argument('--maf',
                            dest='maf',
                            type=float,
                            default=0.05,
                            help='Specify the maf used to filter SNPs, this will be used to remove rare alleles and correct thresholds (default: 0.05)')

        parser.add_argument('--permutation_file',
                            dest='permutation_file',
                            type=str,
                            default=None,
                            help='Specify the file name containing the permutation thresholds used to compute n_hits_perm')

        parser.add_argument('--permutation',
                            dest='permutation',
                            type=float,
                            default=None,
                            help='Specify the permutation threshold (if not providing a permutation_file).')

        parser.add_argument('--genotype_id',
                            dest='genotype_id',
                            type=int,
                            default=None,
                            required = True,
                            help='Specify the id of the related genotype.')
        parser.add_argument('--method',
                            dest='method',
                            type=str,
                            required = True,
                            help='Specify the method used in the GWAS.')
        parser.add_argument('--transformation',
                            dest='transformation',
                            type=str,
                            default=None,
                            required = True,
                            help='Specify the phenotype transformation used before the GWAS.')


    def handle(self, *args, **options):
        hdf5_folder = os.fsencode(options['hdf5_folder'])
        maf = options['maf']
        permutation_file =  options.get('permutation_file', None)
        default_perm_threshold = options.get('permutation', None)
        if default_perm_threshold:
            if default_perm_threshold > 1:
                default_perm_threshold = default_perm_threshold
            else:
                default_perm_threshold = -math.log(default_perm_threshold,10)
        phenotype_id = options.get('phenotype_id', None)
        genotype_id = options.get('genotype_id', None)
        method = options.get('method', None)
        transformation = options.get('transformation', None)
        try:
            # checks
            if None in [genotype_id, method, transformation]:
                raise ValueError("You must provide genotype_id, method and transformation")
            genotype = Genotype.objects.get(pk=genotype_id)
            counter = 0
            if permutation_file:
                permutation_thresholds = load_permutation_thresholds(permutation_file)
            else:
                permutation_thresholds = {}
            files = sorted(os.listdir(hdf5_folder))
            num_files = len(files)
            for file in files:
                filename = os.fsdecode(file)
                try:
                    if not filename.endswith(".hdf5"):
                        continue
                    phenotype_id = filename.split(".")[0]
                    phenotype = Phenotype.objects.get(pk=phenotype_id)

                    perm_threshold = permutation_thresholds.get(phenotype_id, default_perm_threshold)
                    hits, thresholds = get_hit_count(os.path.join(options['hdf5_folder'], filename), maf=maf, perm_threshold=perm_threshold)
                    r = requests.get('https://arapheno.1001genomes.org/rest/phenotype/%s/values.json' % phenotype_id)
                    accessions = r.json()
                    countries = [acc['accession_country'] for acc in accessions]
                    study_name='%s_%s_%s_%s' % (phenotype.name.replace(" ","_"), transformation, genotype.name, method),
                    try:
                        study = Study.objects.get(pk = phenotype_id)
                    except Study.DoesNotExist:
                        study = Study(pk=phenotype_id)
                    study.name = study_name
                    study.transformation=transformation
                    study.genotype=genotype
                    study.phenotype=phenotype
                    study.method=method
                    study.n_hits_bonf=hits['bonferroni_hits05']
                    study.n_hits_thr=hits['thr_e-4']
                    study.n_hits_fdr=hits['bh_hits']
                    study.bonferroni_threshold=thresholds['bonferroni_threshold05']
                    study.bh_threshold=thresholds['bh_threshold']
                    study.n_hits_total=thresholds['total_associations']
                    study.number_samples=len(accessions)
                    study.number_countries=len(set(countries))
                    study.n_hits_perm = hits.get('permutation_hits', None)
                    study.permutation_threshold = thresholds.get('permutation', None)
                    study.save()
                    counter +=1
                    self.stdout.write(self.style.SUCCESS('Study %s(%s) updated (%s/%s finished)' % (study.name, study.pk, counter,num_files)))
                except Exception as err:
                    import pdb ; pdb.set_trace()
                    self.stdout.write(self.style.ERROR('Impossible to update study from file %s. Reason: %s' % (filename, str(err))))
        except Exception as err:
            import pdb ; pdb.set_trace()
            raise CommandError(
                'Error updating studies. Reason: %s' % str(err))

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