from collections import OrderedDict
from rest_framework import serializers
from trustlab.models import Scenario
from trustlab.serializers.string_list_field import StringListField


class ScenarioSerializer(serializers.Serializer):
    name = serializers.CharField()
    agents = StringListField(allow_null=True, required=False)
    observations = serializers.ListField(allow_null=True, required=False)
    scales_per_agent = serializers.DictField(allow_null=True, required=False)
    metrics_per_agent = serializers.DictField(allow_null=True, required=False)
    history = serializers.DictField(allow_null=True, required=False)
    description = serializers.CharField(allow_null=True, allow_blank=True, required=False)
    lazy_note = serializers.CharField(allow_null=True, allow_blank=True, required=False)

    def to_representation(self, instance):
        """
        Delete fields, which are null from representation. Code by https://stackoverflow.com/a/45569581.
        Comment: Might be also good in a own class to represent in several serializers as done in stackoverflow.
        """
        result = super(ScenarioSerializer, self).to_representation(instance)
        return OrderedDict([(key, result[key]) for key in result if result[key] is not None])

    def create(self, validated_data):
        return Scenario(validated_data.get('name'), validated_data.get('agents'), validated_data.get('observations'),
                        validated_data.get('history'), validated_data.get('scales_per_agent'),
                        validated_data.get('metrics_per_agent'), validated_data.get('description', ""))

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.agents = validated_data.get('agents', instance.agents)
        instance.observations = validated_data.get('observations', instance.observations)
        instance.history = validated_data.get('history', instance.history)
        instance.scales_per_agent = validated_data.get('scales_per_agent', instance.scales_per_agent)
        instance.metrics_per_agent = validated_data.get('metrics_per_agent', instance.metrics_per_agent)
        instance.description = validated_data.get('description', instance.description)
        return instance


