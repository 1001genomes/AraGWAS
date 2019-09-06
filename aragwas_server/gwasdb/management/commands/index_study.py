from django.core.management.base import BaseCommand, CommandError
from gwasdb.tasks import index_study
from gwasdb.models import Study
from gwasdb.hdf5 import load_permutation_thresholds
from celery import group


class Command(BaseCommand):
    help = 'Index a GWAS study in elasticsearch'

    def add_arguments(self, parser):
        parser.add_argument('--id',
                            dest='study_id',
                            type=int,
                            default=None,
                            help='Specify a primary key to index a specific study')
        parser.add_argument('--permutations',
                            dest='perm_file',
                            type=str,
                            default=None,
                            help='Specify the file name containing the permutation thresholds')


    def handle(self, *args, **options):
        study_id = options.get('study_id', None)
        perm_file = options.get('perm_file', None)
        try:
            if study_id:
                studies = [Study.objects.get(pk=study_id)]
            else:
                studies = Study.objects.all()
            if perm_file:
                permutation_thresholds = load_permutation_thresholds(perm_file)
            else:
                permutation_thresholds = {}
            num_studies = len(studies)
            counter = 0
            jobs = group(index_study.s(study.pk, permutation_thresholds.get(study.pk,None)) for study in studies)
            result = jobs.apply_async()
            output = result.get()

            for (indexed_assoc, failed_assoc), study_id in output:
                try:
                    if failed_assoc > 0:
                        self.stdout.write(self.style.ERROR('%s/%s Following associations failed to index for "%s" in elasticsearch' % (failed_assoc, indexed_assoc + failed_assoc, study_id)))
                    elif indexed_assoc == 0:
                        self.stdout.write(self.style.WARNING('No associations found that match the threshold. Skipping "%s" in elasticsearch' % study_id))
                    else:
                        self.stdout.write(self.style.SUCCESS('Successfully indexed all %s assocations for "%s" in elasticsearch. (%s/%s finished)' % (indexed_assoc, study_id, counter, num_studies)))
                    counter +=1
                except FileNotFoundError as err:
                        self.stdout.write(self.style.ERROR('HDF5 file for study %s not found' % study))
        except Exception as err:
            raise CommandError(
                'Error indexing GWAS studies. Reason: %s' % str(err))
