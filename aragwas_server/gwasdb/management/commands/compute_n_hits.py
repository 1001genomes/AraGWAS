from django.core.management.base import BaseCommand, CommandError
from gwasdb.hdf5 import get_hit_count, load_permutation_thresholds
from gwasdb.models import Study
from aragwas import settings
import os


class Command(BaseCommand):
    help = 'Fetch number of SNPs passing filtering, adapt bonferroni thresholds and add number of hits'

    def add_arguments(self, parser):
        parser.add_argument('--maf',
                            dest='maf',
                            type=float,
                            default=0.05,
                            help='Specify the maf used to filter SNPs, this will be used to remove rare alleles and correct thresholds (default: 0.05)')
        parser.add_argument('--update_all',
                            dest='update_all',
                            type=bool,
                            default=False,
                            help='Set to true if all studies must be re-updated (default: False)')
        parser.add_argument('--id',
                            dest='study_id',
                            type=int,
                            default=None,
                            help='Specify a primary key to compute for a specific study. If empty will check entire phenotype list.')
        parser.add_argument('--permutations',
                            dest='perm_file',
                            type=str,
                            default=None,
                            help='Specify the file name containing the permutation thresholds used to compute n_hits_perm')

    def handle(self, *args, **options):
        maf = options.get('maf', None)
        update_all = options.get('update_all', None)
        study_id = options.get('study_id', None)
        perm_file = options.get('perm_file', None)
        try:
            if study_id:
                ids_aragwas = [study_id]
            else:
                # Run through all studies with hdf5 files
                ids_aragwas = Study.objects.all().values_list('id', flat=True)
            if perm_file:
                permutation_thresholds = load_permutation_thresholds(perm_file)
            else:
                permutation_thresholds = None
            counter = 0
            for id in ids_aragwas:
                try:
                    study = Study.objects.get(pk=id)
                    if study.n_hits_bonf == None or update_all or study_id: # Condition for first run through, might be changed to update all
                        hdf5_file = os.path.join(settings.HDF5_FILE_PATH, 'gwas_results', '%s.hdf5' % study.pk)
                        perm_threshold = None
                        if permutation_thresholds:
                            perm_threshold = permutation_thresholds[study.pk]
                        hits, thresholds = get_hit_count(hdf5_file, maf=maf, perm_threshold=perm_threshold)
                        study.n_hits_bonf = hits['bonferroni_hits05']
                        study.n_hits_thr = hits['thr_e-4']
                        study.n_hits_fdr = hits['bh_hits']
                        study.bonferroni_threshold = thresholds['bonferroni_threshold05']
                        study.bh_threshold = thresholds['bh_threshold']
                        study.n_hits_total = thresholds['total_associations']
                        if perm_file:
                            study.n_hits_perm = hits['permutation_hits']
                            study.permutation_threshold = thresholds['permutation']
                        study.save()
                        self.stdout.write(self.style.SUCCESS('Study %s successfully updated' % study))
                        counter +=1
                except Exception as err:
                    self.stdout.write(self.style.ERROR('HDF5 file for study %s not found' % study))
            print(str(counter) + ' studies updated in the database.')
        except Exception as err:
            raise CommandError(
                'Error saving phenotypes. Reason: %s' % str(err))