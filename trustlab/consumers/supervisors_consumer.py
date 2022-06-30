from trustlab.consumers.chunk_consumer import ChunkAsyncJsonWebsocketConsumer
from trustlab.models import Supervisor


class SupervisorsConsumer(ChunkAsyncJsonWebsocketConsumer):
    async def connect(self):
        Supervisor.objects.create(channel_name=self.channel_name)
        await self.accept()

    async def disconnect(self, close_code):
        Supervisor.objects.filter(channel_name__exact=self.channel_name).delete()

    async def scenario_registration(self, event):
        await self.send_websocket_message({
            "type": "scenario_registration",
            "scenario": event["scenario"],
            "scenario_run_id": event["scenario_run_id"],
            "agents_at_supervisor": event["agents_at_supervisor"]
        })

    async def scenario_discovery(self, event):
        await self.send_websocket_message({
            "type": "scenario_discovery",
            "scenario_run_id": event["scenario_run_id"],
            "discovery": event["discovery"]
        })

    async def scenario_start(self, event):
        await self.send_websocket_message({
            "type": "scenario_start",
            "scenario_run_id": event["scenario_run_id"],
            "scenario_status": event["scenario_status"]
        })

    async def observation_done(self, event):
        await self.send_websocket_message({
            "type": "observation_done",
            "scenario_run_id": event["scenario_run_id"],
            "observations_done": event["observations_done"]
        })

    async def scenario_end(self, event):
        await self.send_websocket_message({
            "type": "scenario_end",
            "scenario_run_id": event["scenario_run_id"],
            "scenario_status": event["scenario_status"]
        })

    async def receive_json(self, content, **kwargs):
        handled = await super().receive_chunk_ack(content)
        if not handled:
            if content["type"] and content["type"] == "max_agents":
                supervisor = Supervisor.objects.get(channel_name=self.channel_name)
                supervisor.max_agents = content["max_agents"]
                supervisor.ip_address = content["ip_address"]
                if 'hostname' in content:
                    supervisor.hostname = content["hostname"]
                supervisor.save()
                answer = {"type": "max_agents", "status": 200}
                await self.send_json(answer)
            elif content["type"] and (content["type"] == "agent_discovery" or content["type"] == "scenario_end"):
                await self.channel_layer.send(content["scenario_run_id"], content)
            elif content["type"] and content["type"] == "observation_done":
                content["channel_name"] = self.channel_name
                await self.channel_layer.send(content["scenario_run_id"], content)
            else:
                print(content)
                await self.send_json(content)


