from django.core.management.base import BaseCommand, CommandError
from gwasdb.tasks import index_study
from gwasdb.models import Study


class Command(BaseCommand):
    help = 'Index a GWAS study in elasticsearch'

    def add_arguments(self, parser):
        parser.add_argument('--id',
                            dest='study_id',
                            type=int,
                            default=None,
                            help='Specify a primary key to index a specific study')

    def handle(self, *args, **options):
        study_id = options.get('study_id', None)
        try:
            if study_id:
                studies = [Study.objects.get(pk=study_id)]
            else:
                studies = Study.objects.all()
            for study in studies:
                indexed_assoc, failed_assoc = index_study(study.pk)
                if failed_assoc > 0:
                    self.stdout.write(self.style.ERROR('%s/%s SNPs failed to index for "%s" in elasticsearch' % (failed_assoc, indexed_assoc + failed_assoc, study)))
                elif indexed_assoc == 0:
                    self.stdout.write(self.style.WARNING('No associations found that match the threshold. Skipping "%s" in elasticsearch' % (str(study))))
                else:
                    self.stdout.write(self.style.SUCCESS('Successfully indexed all %s assocations for "%s" in elasticsearch' % (indexed_assoc, study)))
        except Exception as err:
            raise CommandError(
                'Error indexing GWAS studies. Reason: %s' % str(err))
