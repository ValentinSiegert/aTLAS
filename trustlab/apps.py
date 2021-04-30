from django.apps import AppConfig


class TrustlabConfig(AppConfig):
    name = 'trustlab'

    # TODO: Handle corner cases i.e. restricting ready method running multiple times. (See AppConfig doc)
    def ready(self):
        Supervisor = self.get_model('Supervisor')
        Supervisor.objects.all().delete()
        print('Outdated supervisors handled')
