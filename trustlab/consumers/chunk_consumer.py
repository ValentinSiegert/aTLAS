import asyncio
import json
from channels.generic.websocket import AsyncJsonWebsocketConsumer
from pympler import asizeof
from trustlab.lab.config import WEBSOCKET_MAX


class ChunkAsyncJsonWebsocketConsumer(AsyncJsonWebsocketConsumer):
    """
    A websocket consumer for async handling with only json messages and the capability of chunked transfer.
    """
    parts_to_send = []

    async def send_websocket_message(self, message):
        """
        Handles all out going websocket messages to not overflow the size of one message handable for the websocket
        connection. Thus, this function introduces chunked transfer of the given message if required. The maximum size
        of one message is set in config with parameter WEBSOCKET_MAX.py

        :param message: The message to be send as JSON object via the websocket connection.
        :type message: dict or list
        """
        message_size = asizeof.asizeof(message)
        if message_size < WEBSOCKET_MAX:
            await self.send_json(message)
        else:
            message_str = json.dumps(message)
            self.parts_to_send = [message_str[i:i + WEBSOCKET_MAX] for i in range(0, len(message_str), WEBSOCKET_MAX)]
            await self.send_part(0)

    async def send_part(self, part_number):
        existing_parts = len(self.parts_to_send)
        if self.parts_to_send and part_number < existing_parts:
            print(f'Transferring part {part_number + 1}/{existing_parts} ...')
            await self.send_json({
                'type': 'chunked_transfer',
                'part_number': (part_number + 1, existing_parts),
                'part': self.parts_to_send[part_number]
            })
            if part_number == existing_parts - 1:
                self.parts_to_send = []

    async def receive_chunk_ack(self, content):
        if content["type"] and content["type"] == "chunked_transfer_ack":
            await self.send_part(content["part_number"][0])
            return True
        else:
            return False
