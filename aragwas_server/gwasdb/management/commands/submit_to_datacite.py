"""
Command Line function to submit Study or Phenotype to datacite
"""
from django.core.management.base import BaseCommand, CommandError
from gwasdb.models import Study
from gwasdb.datacite import submit_to_datacite



class Command(BaseCommand):
    """
    Command to submit GWAS study to datacite
    """
    help = 'Submit a GWAS study to Datacite'

    def add_arguments(self, parser):
        parser.add_argument('--id',
                            dest='entity_id',
                            type=int,
                            default=None,
                            help='Specify a primary key to submit a specific GWAS study')

    def handle(self, *args, **options):
        entity_id = options['entity_id']
        try:
            entities = []
            if entity_id is not None:
                entities = [Study.objects.get(pk=entity_id)]
            else:
                entities = Study.objects.all()
            success = []
            failed = []
            for entity in entities:
                try:
                    resp = submit_to_datacite(entity)
                    success.append((entity, resp))
                except Exception as err:
                    failed.append((entity, str(err)))
            if len(failed) == 0:
                self.stdout.write(self.style.SUCCESS('Successfully submitted %s GWAS studies to datacite' % (len(success))))
            else:
                self.stdout.write(self.style.WARNING('Failed to submit %s of %s GWAS studies to datacite' % (len(failed), len(entities))))
            for resp in failed:
                self.stdout.write(self.style.ERROR('%s: %s' % (resp[0], resp[1])))
            self.stdout.write('------------------------------------')
            for resp in success:
                self.stdout.write(self.style.SUCCESS('%s: %s' % (resp[0], resp[1])))

        except Exception as err:
            raise CommandError('Error submitting GWAS studies to datacite. Reason: %s' % str(err))