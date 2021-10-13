from rest_framework import serializers
from trustlab.models import Scenario
from trustlab.serializers.string_list_field import StringListField


class ScenarioSerializer(serializers.Serializer):
    name = serializers.CharField()
    agents = StringListField()
    observations = serializers.ListField()
    scales_per_agent = serializers.DictField()
    metrics_per_agent = serializers.DictField()
    history = serializers.DictField()
    description = serializers.CharField(allow_null=True, allow_blank="True")

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


