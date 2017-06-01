from django.core.checks import Error,Warning, register
from gwasdb import elastic

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
