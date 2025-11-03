from abc import ABC, abstractmethod
import asyncio

class SenseModule(ABC):
    def __init__(self, model_responder, shutdown_event: asyncio.Event):
        self.model_responder = model_responder
        self.shutdown_event = shutdown_event
        self.logger = None # Will be set by the factory

    @abstractmethod
    async def start(self):
        pass

    async def stop(self):
        pass
