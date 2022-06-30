from django.views import generic
from trustlab.models import *
from trustlab.serializers.scenario_serializer import ScenarioSerializer
from rest_framework.renderers import JSONRenderer
from rest_framework.reverse import reverse
from trustlab_host.config import ATLAS_VERSION
import trustlab.lab.config as config


class IndexView(generic.TemplateView):
    template_name = 'index.html'

    def get_context_data(self, **kwargs):
        # call the base implementation first to get a context
        context = super().get_context_data(**kwargs)
        context["atlas_version"] = ATLAS_VERSION
        if config.EVALUATION_SCRIPT_RUNS:
            context['eval_run'] = True
        else:
            context['eval_run'] = False
            # add saved Scenarios
            try:
                # ScenarioFactory throws AssertionError if no predefined scenarios could be loaded
                scenario_factory = ScenarioFactory(lazy_load=True)
                context['scenario_categories'] = scenario_factory.get_scenarios_in_categories()
                # for manipulation of scenarios via JS, send them also as JSON
                scenario_serializer = ScenarioSerializer(scenario_factory.scenarios, many=True)
                context["scenarios_JSON"] = JSONRenderer().render(scenario_serializer.data).decode('utf-8')
                # add URL of index.html to PUT scenario
                context["index_url"] = reverse('index')
                context["lab_url"] = reverse('lab')
            except AssertionError:
                context["ScenarioLoadError"] = f"No predefined scenarios could be loaded!"
        return context

    # currently unused method
    # def put(self, request, *args, **kwargs):
    #     json_scenario = json.loads(request.body.decode())
    #     serializer = ScenarioSerializer(data=json_scenario)
    #     if serializer.is_valid():
    #         try:
    #             scenario_factory = ScenarioFactory()
    #             scenario = serializer.create(serializer.data)
    #         except ValueError as value_error:
    #             return HttpResponse(str(value_error), status=400)
    #         return HttpResponse("Starting Lab Runtime according to Scenario", status=200) \
    #             if scenario in scenario_factory.scenarios \
    #             else HttpResponse("Scenario not found!", status=404)
    #     return HttpResponse(serializer.errors, status=400)



