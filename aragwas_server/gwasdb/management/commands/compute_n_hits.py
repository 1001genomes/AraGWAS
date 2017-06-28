from django.core.management.base import BaseCommand, CommandError
from gwasdb.hdf5 import get_hit_count
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

    def handle(self, *args, **options):
        maf = options.get('maf', None)
        update_all = options.get('update_all', None)
        study_id = options.get('study_id', None)
        try:
            if study_id:
                ids_aragwas = [study_id]
            else:
                # Run through all studies with hdf5 files
                ids_aragwas = Study.objects.all().values_list('id', flat=True)
            counter = 0
            for id in ids_aragwas:
                try:
                    study = Study.objects.get(pk=id)
                    if study.n_hits_bonf == None or update_all: # Condition for first run through, might be changed to update all
                        hdf5_file = os.path.join(settings.HDF5_FILE_PATH, '%s.hdf5' % study.pk)
                        hits, thresholds = get_hit_count(hdf5_file, maf=maf)
                        study.n_hits_bonf = hits['bonferroni_hits05']
                        study.n_hits_top = hits['thr_e-4']
                        study.n_hits_fdr = hits['bh_hits']
                        study.save()
                        counter +=1
                except FileNotFoundError as err:
                    self.stdout.write(self.style.ERROR('HDF5 file for study %s not found' % study))
            print(str(counter) + ' studies updated in the database.')
        except Exception as err:
            raise CommandError(
                'Error saving phenotypes. Reason: %s' % str(err))