from django.core.checks import Error, Warning, register
from gwasdb import elastic
from aragwas import settings

@register()
def check_elasticsearch(app_configs, **kwargs):
    errors = []

    is_running = elastic.check_server()
    if not is_running:
        errors.append(
                Error(
                    'Elasticsearch node is not running',
                    hint='Start the elasticsearch container with docker-compose up -d elasticsearch1',
                    obj=None,
                    id='gwasdb.E001',
                )
        )
    else:
        try:
            elastic.check_genotype_data()
        except Exception as err:
            errors.append(
                Warning(
                    'Genotype data has not been indexed in elasticsearch. Reason: %s' % str(err),
                    hint='Run the init_elasticsearch.sh script',
                    obj=None,
                    id='gwasdb.E002',
                )
            )
    return errors

@register()
def check_datacite(app_configs, **kwargs):
    errors = []
    CheckObj = Error
    if settings.DEBUG:
        CheckObj = Warning
    if not settings.DATACITE_USERNAME:
        errors.append(CheckObj('No DATACITE_USERNAME specified',
            hint='Set the environment variable DATACITE_USERNAME before starting the backend if you want to register DOIs',
            obj=None, id='gwasdb.E002'))
    if not settings.DATACITE_PASSWORD:
        errors.append(CheckObj('No DATACITE_PASSWORD specified',
            hint='Set the environment variable DATACITE_PASSWORD before starting the backend if you want to register DOIs',
            obj=None, id='gwasdb.E002'))
    return errors
