import asyncio
import inspect
import json
import uuid
from base64 import b64decode, b64encode
from itertools import cycle
from types import FunctionType
from typing import TypeAlias

import requests
import websockets

JSON: TypeAlias = dict[str, "JSON"] | list["JSON"] | str | int | float | bool | None


def split(a, n):
    """Splits given array into n equal chunks of length"""
    k, m = divmod(len(a), n)
    return [a[i * k + min(i, m):(i + 1) * k + min(i + 1, m)] for i in range(n)]


class FlowQlient:
    """FlowQlient is an API to connect and command the cluster"""

    def __init__(self, channel: str):
        self.websocket = None
        self.name = None
        self.workers = []
        self.channel = channel
        self.uri = "wss://hack.chat/chat-ws"
        self.location = str(uuid.uuid4())
        self.base_url = f"https://filebin.net/{self.location}"
        self.task_pending = []
        self.collected_tasks = []
        self.delay = 6
        print(self.base_url)

    def upload(self, data: JSON):
        """Uploads the data to the FileBin Server"""
        url = self.base_url + "/input.json"
        requests.post(url, json=data)

    def download(self, bot: str) -> JSON:
        """Downloads the data from the FileBin Server"""
        return requests.get(self.base_url + "/" + bot).json()

    def connect(self, name: str):
        """Initializes the Connection to HackChat for communication with the cluster"""
        self.name = name

        async def setup_connection():
            self.websocket = await websockets.connect(self.uri)
            conn = json.dumps({"cmd": "join", "channel": self.channel, "nick": self.name})
            await self.websocket.send(conn)
            await self.get_available_workers()

        asyncio.get_event_loop().run_until_complete(setup_connection())

    def send(self, payload):
        """Sends the payload to the HackChat Server"""
        data = b64encode(payload.encode()).decode()

        async def send(data):
            await self.websocket.send(json.dumps({"cmd": "chat", "text": data}))

        asyncio.get_event_loop().run_until_complete(send(self, data))

    def get(self, tasks: list):
        """The Function to execute the given tasks in Cluster"""
        async def send_task(all_tasks):
            payload = {}
            for i in self.workers:
                payload[i] = []
            for task, worker in zip(tasks, cycle(self.workers)):
                payload[worker].append(task)
                self.task_pending.append(task["task_id"])
            self.upload(payload)
            data = b64encode(self.location.encode()).decode()
            await self.websocket.send(json.dumps({"cmd": "chat", "text": data}))

        async def collect_results():
            collected_tasks = {}
            while len(collected_tasks) != len(tasks):
                data = await self.websocket.recv()
                payload = json.loads(data)
                if payload["cmd"] == "chat" and "bot" in payload["nick"]:
                    bot = (b64decode(payload["text"]).decode())
                    data = self.download(bot)
                    collected_tasks.update(data)
                elif payload["cmd"] == "warn":
                    print(payload["text"])
            return collected_tasks

        fut = asyncio.gather(send_task(tasks), collect_results())
        out = asyncio.get_event_loop().run_until_complete(fut)
        results = []
        for task in tasks:
            results.append(out[1][task["task_id"]])

        return results

    def task(self, func: FunctionType) -> JSON:
        """A decorator function that converts the function into a task"""
        def wrap(*args: list, **kwargs: dict) -> JSON:
            code = (inspect.getsource(func))
            code = code[code.find("def"):]
            args = list(args)
            task_id = str(uuid.uuid4())
            payload = {"task_id": task_id, "code": code, "args": args, "kwargs": kwargs}
            return payload

        return wrap

    async def get_available_workers(self) -> list:
        """Gets all the available workers"""
        data = await self.websocket.recv()
        payload = json.loads(data)
        if payload["cmd"] == "onlineSet":
            for i in payload["nicks"]:
                if "bot" in i:
                    self.workers.append(i)
        return self.workers
