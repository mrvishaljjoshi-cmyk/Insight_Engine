from abc import ABC, abstractmethod
from typing import List, Dict, Any

class BaseBrokerProvider(ABC):
    @abstractmethod
    def fetch_holdings(self) -> List[Dict[str, Any]]:
        pass
    
    @abstractmethod
    def get_ltp(self, symbol: str) -> float:
        pass

    @abstractmethod
    def authenticate(self, credentials: Dict[str, Any]) -> str:
        """Returns access token"""
        pass
