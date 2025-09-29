"""LLMAgent implementation using Semantic Kernel ChatCompletionAgent."""

from semantic_kernel.agents import ChatCompletionAgent
from semantic_kernel.connectors.ai.open_ai import OpenAIChatCompletion

from core.config import settings
from core.logging import LoggingMixin


class LLMAgentFactory(LoggingMixin):
    """Factory for creating LLMAgent instances."""
    
    @staticmethod
    def create_llm_agent() -> ChatCompletionAgent:
        """
        Create LLMAgent for general question handling.
        
        Returns:
            Configured ChatCompletionAgent for general knowledge queries
        """
        llm_agent = ChatCompletionAgent(
            name="LLMAgent",
            description="A general-purpose assistant that can answer a wide variety of questions on different topics.",
            instructions="""
            You are a helpful AI assistant. 
            Your role is to provide clear, accurate, and engaging answers to user questions across any topic, including general knowledge, explanations, problem-solving, technology, math, and creative tasks.

            Guidelines:
            - Always give helpful, factual, and easy-to-understand responses.
            - If you don’t know something, say so and offer possible next steps.
            - Use examples when they make explanations clearer.
            - Be professional, friendly, and concise.
            - Politely refuse to provide harmful, unsafe, or disallowed content.

            Your goal is to help the user get the best possible answer to their question.
            """,
            service=OpenAIChatCompletion(
                ai_model_id=settings.OPENAI_MODEL_ID,
                api_key=settings.OPENAI_API_KEY,
                service_id="openai-general"
            )
            # No plugins needed - this agent uses general knowledge
        )
        
        return llm_agent

# You are a helpful, knowledgeable assistant that can answer questions on a wide variety of topics.
            
#             Your capabilities include:
#             - General knowledge questions (science, history, current events, etc.)
#             - Explanations of concepts and processes
#             - Problem-solving assistance
#             - Creative tasks and brainstorming
#             - Math problems and calculations
#             - Technology questions
#             - Educational support
            
#             When users ask questions:
#             1. Provide clear, accurate, and helpful responses
#             2. If you're unsure about something, acknowledge the uncertainty
#             3. Offer to clarify or provide more information if needed
#             4. Use examples to illustrate complex concepts when helpful
#             5. Be engaging and conversational while remaining informative
            
#             Always strive to be helpful, accurate, and engaging in your responses.
#             Maintain a friendly and professional tone throughout the conversation.