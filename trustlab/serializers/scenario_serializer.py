from rest_framework import serializers
from trustlab.models import Scenario
from trustlab.serializers.stringList_field import StringListField


class ScenarioSerializer(serializers.Serializer):
    name = serializers.CharField()
    agents = StringListField()
    observations = serializers.ListField()
    authorities = serializers.DictField()
    topics = serializers.DictField()
    trust_thresholds = serializers.DictField()
    weights = serializers.DictField()
    metrics_per_agent = serializers.DictField()
    history = serializers.DictField()
    description = serializers.CharField(allow_null=True, allow_blank="True")

    def create(self, validated_data):
        return Scenario(validated_data.get('name'), validated_data.get('agents'), validated_data.get('observations'),
                        validated_data.get('history'), validated_data.get('trust_thresholds'),
                        validated_data.get('weights'), validated_data.get('metrics_per_agent'),
                        validated_data.get('authorities'), validated_data.get('topics'),
                        validated_data.get('description', ""))

    def update(self, instance, validated_data):
        instance.name = validated_data.get('name', instance.name)
        instance.agents = validated_data.get('agents', instance.agents)
        instance.observations = validated_data.get('observations', instance.observations)
        instance.history = validated_data.get('history', instance.history)
        instance.trust_thresholds = validated_data.get('trust_thresholds', instance.trust_thresholds)
        instance.weights = validated_data.get('weights', instance.weights)
        instance.metrics_per_agent = validated_data.get('metrics_per_agent', instance.metrics_per_agent)
        instance.authorities = validated_data.get('authorities', instance.authorities)
        instance.topics = validated_data.get('topics', instance.topics)
        instance.description = validated_data.get('description', instance.description)
        return instance


