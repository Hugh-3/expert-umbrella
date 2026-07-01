from abc import ABC, abstractmethod
from typing import Any, Dict

class BaseAgent(ABC):
    """智能体基类"""
    
    def __init__(self, config: Dict[str, Any]):
        self.config = config
    
    @abstractmethod
    async def run(self, *args, **kwargs) -> Dict[str, Any]:
        """执行智能体任务"""
        pass
    
    def _validate_config(self, required_keys: list):
        for key in required_keys:
            if key not in self.config:
                raise ValueError(f"Missing required config key: {key}")
