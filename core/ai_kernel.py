"""Semantic Kernel factory for AI operations."""

from typing import Optional
from semantic_kernel import Kernel
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion
from semantic_kernel.contents.chat_history import ChatHistory
from semantic_kernel.connectors.ai.open_ai.prompt_execution_settings.open_ai_prompt_execution_settings import OpenAIChatPromptExecutionSettings
from pydantic import BaseModel

from core.config import settings


class AIKernelFactory:
    """Factory for creating and managing Semantic Kernel instances."""
    
    _kernel: Optional[Kernel] = None
    
    @classmethod
    def get_kernel(cls) -> Kernel:
        """
        Get or create a Semantic Kernel instance.
        
        Returns:
            Configured Kernel instance with OpenAI chat completion
        """
        if cls._kernel is None:
            cls._kernel = cls._create_kernel()
        return cls._kernel
    
    @classmethod
    def _create_kernel(cls) -> Kernel:
        """
        Create a new Semantic Kernel instance.
        
        Returns:
            Configured Kernel instance
        """
        # Validate OpenAI API key
        if not settings.OPENAI_API_KEY:
            raise ValueError(
                "OPENAI_API_KEY environment variable is required but not set. "
                "Please set your OpenAI API key in your environment or .env.local file."
            )
        
        # Initialize the kernel
        kernel = Kernel()
        
        # Create OpenAI chat completion service
        try:
            chat_completion_service = OpenAIChatCompletion(
                ai_model_id="gpt-4o-mini",
                api_key=settings.OPENAI_API_KEY,
                service_id="openai-chat"
            )
        except Exception as e:
            raise ValueError(
                f"Failed to initialize OpenAI service. "
                f"Please check your OPENAI_API_KEY: {str(e)}"
            )
        
        # Add the chat completion service to the kernel
        kernel.add_service(chat_completion_service)
        
        return kernel
    
    @classmethod
    def get_execution_settings(cls) -> OpenAIChatPromptExecutionSettings:
        """
        Get default execution settings for OpenAI chat completion.
        
        Returns:
            OpenAI chat prompt execution settings
        """
        return OpenAIChatPromptExecutionSettings(
            max_tokens=1000,
            temperature=0.7,
            top_p=1.0,
            frequency_penalty=0.0,
            presence_penalty=0.0
        )
    
    @classmethod
    def get_json_execution_settings(cls, response_schema: type[BaseModel] | None = None) -> OpenAIChatPromptExecutionSettings:
        """
        Get execution settings for JSON response format.
        
        Returns:
            OpenAI chat prompt execution settings configured for JSON output
        """
        settings = cls.get_execution_settings()
        if response_schema:
            settings.response_format = response_schema
        else:
            settings.response_format = {"type": "json_object"}
        settings.structured_json_response = True
        return settings
    
    @classmethod
    def create_chat_history(cls, system_message: Optional[str] = None) -> ChatHistory:
        """
        Create a new chat history with optional system message.
        
        Args:
            system_message: Optional system message to start the conversation
            
        Returns:
            ChatHistory instance
        """
        history = ChatHistory()
        
        if system_message:
            history.add_system_message(system_message)
            
        return history


# Convenience function for getting kernel instance
def get_kernel() -> Kernel:
    """Get the Semantic Kernel instance."""
    return AIKernelFactory.get_kernel()


# Convenience function for getting execution settings
def get_execution_settings() -> OpenAIChatPromptExecutionSettings:
    """Get default execution settings."""
    return AIKernelFactory.get_execution_settings()


# Convenience function for getting JSON execution settings
def get_json_execution_settings(response_schema: type[BaseModel] | None = None) -> OpenAIChatPromptExecutionSettings:
    """Get JSON execution settings."""
    return AIKernelFactory.get_json_execution_settings(response_schema=response_schema)
