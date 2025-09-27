"""AI endpoints for API version 1."""

import json
from typing import AsyncIterator
from fastapi import APIRouter, Depends, Query
from fastapi.responses import StreamingResponse
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from core.logging import api_logger
from domain.schemas import FilmSummary, FilmSummaryRequest
from services.ai_service import AIService


router = APIRouter(prefix="/ai", tags=["ai"])


def get_ai_service() -> AIService:
    """Get AI service instance."""
    return AIService()


@router.get("/ask")
async def ask_question(
    question: str = Query(..., min_length=1, description="Question to ask the AI"),
    service: AIService = Depends(get_ai_service)
):
    """
    Stream AI response to user question using Server-Sent Events (SSE).
    
    **Query Parameters:**
    - **question**: The question to ask the AI (minimum 1 character)
    
    **Response:**
    Streams response chunks using Server-Sent Events for real-time communication.
    
    **Example Usage:**
    ```bash
    curl -H "Accept: text/event-stream" \
         "http://localhost:8000/api/v1/ai/ask?question=What%20movies%20do%20you%20recommend?"
    ```
    
    **JavaScript Usage:**
    ```javascript
    const eventSource = new EventSource('/api/v1/ai/ask?question=What movies do you recommend?');
    
    eventSource.onmessage = function(event) {
        const data = JSON.parse(event.data);
        console.log('AI Response:', data.content);
    };
    
    eventSource.addEventListener('start', function(event) {
        console.log('AI started processing...');
    });
    
    eventSource.addEventListener('complete', function(event) {
        console.log('AI completed response');
        eventSource.close();
    });
    
    eventSource.addEventListener('error', function(event) {
        console.error('AI error:', event.data);
        eventSource.close();
    });
    ```
    
    **SSE Event Types:**
    - `message`: Response content chunks
    - `start`: Processing started
    - `complete`: Response completed
    - `error`: Error occurred
    """
    async def generate_sse_response() -> AsyncIterator[str]:
        """Generate Server-Sent Events response."""
        try:
            api_logger.info("Starting SSE AI response", question_length=len(question))
            
            # Send start event
            yield f"event: start\ndata: {json.dumps({'status': 'processing', 'question': question})}\n\n"
            
            # Stream AI response chunks
            full_response = ""
            chunk_count = 0
            async for chunk in service.ask_question(question):
                if chunk and chunk.strip():
                    full_response += chunk
                    chunk_count += 1
                    # Send message event with chunk
                    chunk_data = {
                        "type": "chunk",
                        "content": chunk,
                        "partial_response": full_response
                    }
                    yield f"event: message\ndata: {json.dumps(chunk_data)}\n\n"
            
            # Send completion event
            completion_data = {
                "type": "complete",
                "full_response": full_response,
                "status": "completed"
            }
            yield f"event: complete\ndata: {json.dumps(completion_data)}\n\n"
            
            api_logger.info(
                "SSE AI response completed", 
                chunk_count=chunk_count, 
                response_length=len(full_response),
                question_length=len(question)
            )
            
        except Exception as e:
            api_logger.error("SSE AI response failed", error=str(e), question_length=len(question))
            # Send error event
            error_data = {
                "type": "error",
                "error": "Failed to process question",
                "details": str(e)
            }
            yield f"event: error\ndata: {json.dumps(error_data)}\n\n"

    return StreamingResponse(
        generate_sse_response(),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "Connection": "keep-alive",
            "Access-Control-Allow-Origin": "*",
            "Access-Control-Allow-Headers": "Cache-Control"
        }
    )


@router.post("/summary", response_model=FilmSummary)
async def summarize_film(
    request: FilmSummaryRequest,
    session: AsyncSession = Depends(get_db_session),
    service: AIService = Depends(get_ai_service)
) -> FilmSummary:
    """
    Generate structured film summary and recommendation.
    
    **Request Body:**
    ```json
    {
        "film_id": 1
    }
    ```
    
    **Response:**
    Returns structured JSON with film analysis:
    ```json
    {
        "title": "Film Title",
        "rating": "PG-13",
        "recommended": true
    }
    ```
    
    **Business Logic:**
    - Recommendation is `true` if rating is more mature than PG-13 (R, NC-17) AND rental_rate < $3.00
    - Uses Semantic Kernel with JSON response format to ensure structured output
    - Looks up film details from the database
    
    **Example Usage:**
    ```bash
    curl -X POST "http://localhost:8000/api/v1/ai/summary" \
         -H "Content-Type: application/json" \
         -d '{"film_id": 1}'
    ```
    """
    api_logger.info("Film summary requested", film_id=request.film_id)
    result = await service.summarize_film(session, request)
    api_logger.info("Film summary completed", film_id=request.film_id, recommended=result.recommended)
    return result
