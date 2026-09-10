from abc import ABC, abstractmethod
from pydantic import BaseModel
class BaseLLMProvider(ABC):
    name = 'unconfigured'
    @abstractmethod
    def structured(self, prompt: str, schema: type[BaseModel]) -> BaseModel: ...
