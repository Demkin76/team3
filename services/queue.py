import asyncio
import logging
from typing import Optional
import redis

from core.config import settings
from agents.agent1_parser import agent1_run
from agents.agent2_cache import agent2_run
from agents.agent3_hunter import agent3_run

log = logging.getLogger("queue")

class QueueService:
    _instance: Optional["QueueService"] = None

    @classmethod
    def get(cls):
        if not cls._instance:
            cls._instance = QueueService()
        return cls._instance

    def __init__(self):
        self.use_redis = settings.USE_REDIS_QUEUE and settings.REDIS_URL
        self.redis = redis.Redis.from_url(settings.REDIS_URL) if self.use_redis else None
        self._tasks = []
        self._stop = asyncio.Event()
        self.q1 = asyncio.Queue()
        self.q2 = asyncio.Queue()
        self.q3 = asyncio.Queue()

    def enqueue_agent1(self, request_id: str):
        if self.use_redis:
            self.redis.lpush("agent1_queue", request_id)
        else:
            self.q1.put_nowait(request_id)

    def enqueue_agent2(self, request_id: str):
        if self.use_redis:
            self.redis.lpush("agent2_queue", request_id)
        else:
            self.q2.put_nowait(request_id)

    def enqueue_agent3(self, request_id: str):
        if self.use_redis:
            self.redis.lpush("agent3_queue", request_id)
        else:
            self.q3.put_nowait(request_id)

    async def _redis_worker(self, queue_name: str, handler):
        while not self._stop.is_set():
            item = self.redis.brpop(queue_name, timeout=1)
            if not item:
                continue
            _, request_id = item
            request_id = request_id.decode()
            try:
                await handler(request_id)
            except Exception as e:
                log.exception("Worker error on %s: %s", queue_name, e)

    async def _local_worker(self, q: asyncio.Queue, handler):
        while not self._stop.is_set():
            try:
                request_id = await asyncio.wait_for(q.get(), timeout=1)
            except asyncio.TimeoutError:
                continue
            try:
                await handler(request_id)
            except Exception as e:
                log.exception("Worker error: %s", e)

    def start_workers(self):
        if self.use_redis:
            self._tasks = [
                asyncio.create_task(self._redis_worker("agent1_queue", agent1_run)),
                asyncio.create_task(self._redis_worker("agent2_queue", agent2_run)),
                asyncio.create_task(self._redis_worker("agent3_queue", agent3_run)),
            ]
        else:
            self._tasks = [
                asyncio.create_task(self._local_worker(self.q1, agent1_run)),
                asyncio.create_task(self._local_worker(self.q2, agent2_run)),
                asyncio.create_task(self._local_worker(self.q3, agent3_run)),
            ]
        log.info("Workers started (redis=%s)", self.use_redis)

    async def stop_workers(self):
        self._stop.set()
        for t in self._tasks:
            t.cancel()
        self._tasks.clear()
