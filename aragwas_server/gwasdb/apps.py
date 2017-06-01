from django.apps import AppConfig





class GwasdbConfig(AppConfig):
    name = 'gwasdb'

    def ready(self):
        super(GwasdbConfig, self).ready()
        # import myapp.signals
        import gwasdb.checks
