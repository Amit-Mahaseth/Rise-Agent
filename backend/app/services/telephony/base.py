from abc import ABC, abstractmethod
from dataclasses import dataclass, field
from typing import Any


@dataclass(slots=True)
class CallProviderResponse:
    provider_call_id: str | None
    status: str
    details: dict[str, Any] = field(default_factory=dict)


class BaseCallProvider(ABC):
    @abstractmethod
    def initiate_outbound_call(self, *, lead_id: str, call_id: str, phone_number: str) -> CallProviderResponse:
        raise NotImplementedError

