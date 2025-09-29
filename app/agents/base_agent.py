"""Base agent framework for consistent agent implementation."""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from semantic_kernel import Kernel
from core.logging import LoggingMixin


class BaseAgent(LoggingMixin, ABC):
    """
    Abstract base class for all agents in the system.
    
    This class provides common functionality and enforces consistent
    interface across all agent implementations.
    """
    
    def __init__(self, kernel: Kernel, agent_name: str):
        """
        Initialize base agent.
        
        Args:
            kernel: Semantic Kernel instance
            agent_name: Name of the agent for logging and identification
        """
        super().__init__()
        self.kernel = kernel
        self.agent_name = agent_name
        self.logger.info("Agent initialized", agent_name=agent_name)
        
    @abstractmethod
    async def can_handle(self, question: str) -> bool:
        """
        Determine if this agent can handle the given question.
        
        Args:
            question: User question to evaluate
            
        Returns:
            True if agent can handle the question, False otherwise
        """
        pass
        
    @abstractmethod
    async def process_question(
        self, 
        question: str, 
        context: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Process the question and return response.
        
        Args:
            question: User question to process
            context: Optional context information
            
        Returns:
            Dictionary containing response content and metadata
        """
        pass
        
    def get_agent_info(self) -> Dict[str, Any]:
        """
        Get agent information for debugging and monitoring.
        
        Returns:
            Dictionary with agent details
        """
        return {
            "name": self.agent_name,
            "type": self.__class__.__name__,
            "kernel_available": self.kernel is not None
        }
