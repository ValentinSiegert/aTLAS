import json
from asgiref.sync import async_to_sync, sync_to_async
from trustlab.lab.connectors.basic_connector import BasicConnector
from django.db import transaction
from django.db.models import F, Sum
from trustlab.models import Supervisor
from channels.layers import get_channel_layer


class ChannelsConnector(BasicConnector):
    @sync_to_async
    def sums_agent_numbers(self):
        return Supervisor.objects.aggregate(sum_max_agents=Sum('max_agents'), sum_agents_in_use=Sum('agents_in_use'))

    @sync_to_async
    def list_supervisors_with_free_agents(self):
        return list(set(Supervisor.objects.filter(agents_in_use__lt=F('max_agents'))))

    @sync_to_async
    def get_supervisors_without_given(self, given_channel_name):
        return list(set(Supervisor.objects.exclude(channel_name=given_channel_name)))

    async def send_message_to_supervisor(self, channel_name, message):
        channel_layer = get_channel_layer()
        await channel_layer.send(channel_name, message)

    async def receive_with_scenario_run_id(self, scenario_run_id):
        channel_layer = get_channel_layer()
        response = await channel_layer.receive(scenario_run_id)
        return response

    @sync_to_async
    @transaction.atomic
    def reserve_agents_in_db(self, distribution):
        for channel_name in distribution.keys():
            supervisor = Supervisor.objects.get(channel_name=channel_name)
            supervisor.agents_in_use += len(distribution[channel_name])
            supervisor.save()

    async def reserve_agents(self, distribution, scenario_run_id, scenario_data):
        discovery = {}
        for channel_name in distribution.keys():
            # init agents at supervisors
            registration_message = {
                "type": "scenario.registration",
                "scenario": scenario_data,
                "scenario_run_id": scenario_run_id,
                "agents_at_supervisor": distribution[channel_name]
            }
            await self.send_message_to_supervisor(channel_name, registration_message)
            agent_discovery = await self.receive_with_scenario_run_id(scenario_run_id)
            discovery = {**discovery, **agent_discovery["discovery"]}
        await self.reserve_agents_in_db(distribution)
        # after registration and discovery knowledge share discovery with all involved supervisors
        discovery_message = {
            "type": "scenario.discovery",
            "scenario_run_id": scenario_run_id,
            "discovery": discovery
        }
        for channel_name in distribution.keys():
            await self.send_message_to_supervisor(channel_name, discovery_message)
        return discovery

    async def start_scenario(self, involved_supervisors, scenario_run_id):
        start_message = {
            "type": "scenario.start",
            "scenario_run_id": scenario_run_id,
            "scenario_status": "started"
        }
        for channel_name in involved_supervisors:
            await self.send_message_to_supervisor(channel_name, start_message)

    async def get_next_done_observation(self, scenario_run_id):
        return await self.receive_with_scenario_run_id(scenario_run_id)

    async def broadcast_done_observation(self, scenario_run_id, done_observations_with_id, supervisors_to_inform):
        done_message = {
            "type": "observation.done",
            "scenario_run_id": scenario_run_id,
            "observations_done": done_observations_with_id
        }
        for supervisor in supervisors_to_inform:
            await self.send_message_to_supervisor(supervisor.channel_name, done_message)

    @sync_to_async
    @transaction.atomic
    def free_agents_in_db(self, distribution):
        for channel_name in distribution.keys():
            supervisor = Supervisor.objects.get(channel_name=channel_name)
            supervisor.agents_in_use -= len(distribution[channel_name])
            supervisor.save()

    async def end_scenario(self, distribution, scenario_run_id):
        end_message = {
            "type": "scenario.end",
            "scenario_run_id": scenario_run_id,
            "scenario_status": "finished"
        }
        for channel_name in distribution.keys():
            await self.send_message_to_supervisor(channel_name, end_message)
            response = await self.receive_with_scenario_run_id(scenario_run_id)
            # print(f"Scenario ended at supervisor '{channel_name}' with message: {response}")
        await self.free_agents_in_db(distribution)



