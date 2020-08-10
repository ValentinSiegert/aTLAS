from trustlab.models import ScenarioFactory
from trustlab.serializers.scenario_serializer import ScenarioSerializer
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status

class ScenariosAPI(APIView):
    """
    List all saved Scenarios by using ScenarioFactory or stores send Scenario
    """
    def get(self, request, format=None):
        scenario_factory = ScenarioFactory()
        query = request.query_params.get('query', None)
        if query is not None:
            # TODO implement filtering of scenarios
            pass
        serializer = ScenarioSerializer(scenario_factory.scenarios, many=True)
        return Response(serializer.data)

    def post(self, request, format=None):
        """
        Assumption: only one scenario is send via a post message, not a bulk of scenarios
        :param request:
        :param format:
        :return:
        """
        serializer = ScenarioSerializer(data=request.data)
        if serializer.is_valid():
            try:
                scenario_factory = ScenarioFactory()
                scenario = serializer.create(serializer.data)
                scenario_factory.scenarios.append(scenario)
            except ValueError as value_error:
                return Response(str(value_error), status=status.HTTP_400_BAD_REQUEST)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)



