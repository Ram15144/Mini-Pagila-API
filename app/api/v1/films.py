"""Film endpoints for API version 1."""

from typing import Optional
from fastapi import APIRouter, Depends, Query
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from domain.schemas import (
    FilmListResponse, 
    FilmResponse, 
    FilmQuery, 
    ErrorResponse, 
    ValidationErrorResponse
)
from services.film_service import FilmService
from repositories.film_repository import FilmRepository


router = APIRouter(prefix="/films", tags=["films"])


def get_film_repository() -> FilmRepository:
    """Get film repository instance."""
    return FilmRepository()


def get_film_service(
    repository: FilmRepository = Depends(get_film_repository)
) -> FilmService:
    """Get film service instance."""
    return FilmService(repository)


@router.get(
    "",
    response_model=FilmListResponse,
    summary="List Films",
    description="Retrieve a paginated list of films with optional category filtering",
    responses={
        200: {
            "description": "Successfully retrieved films list",
            "model": FilmListResponse
        },
        422: {
            "description": "Validation error in query parameters",
            "model": ValidationErrorResponse
        }
    }
)
async def list_films(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    category: Optional[str] = Query(None, description="Filter by category name"),
    session: AsyncSession = Depends(get_db_session),
    service: FilmService = Depends(get_film_service)
) -> FilmListResponse:
    """
    List films with pagination and optional category filtering.
    
    Retrieves a paginated list of films from the catalog. Supports filtering by category name
    using case-insensitive partial matching.
    
    **Query Parameters:**
    - **skip**: Number of records to skip for pagination (default: 0)
    - **limit**: Maximum number of records to return (default: 10, max: 100)
    - **category**: Optional category name filter (e.g., "Action", "Comedy")
    
    **Returns:**
    Paginated list of films with metadata including total count, skip, and limit values.
    
    **Example Usage:**
    - Get first 10 films: `GET /api/v1/films`
    - Get next 10 films: `GET /api/v1/films?skip=10&limit=10`
    - Filter by category: `GET /api/v1/films?category=Action`
    """
    query = FilmQuery(skip=skip, limit=limit, category=category)
    return await service.list_films(session, query)


@router.get(
    "/{film_id}",
    response_model=FilmResponse,
    summary="Get Film by ID",
    description="Retrieve detailed information about a specific film",
    responses={
        200: {
            "description": "Film found and returned successfully",
            "model": FilmResponse
        },
        404: {
            "description": "Film not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not Found",
                        "detail": "Film with ID 999 not found",
                        "status_code": 404
                    }
                }
            }
        },
        422: {
            "description": "Invalid film ID format",
            "model": ValidationErrorResponse
        }
    }
)
async def get_film(
    film_id: int,
    session: AsyncSession = Depends(get_db_session),
    service: FilmService = Depends(get_film_service)
) -> FilmResponse:
    """
    Get detailed information about a specific film by its ID.
    
    Retrieves comprehensive film information including title, description, release year,
    rental details, rating, and other metadata.
    
    **Path Parameters:**
    - **film_id**: The unique identifier of the film (must be a positive integer)
    
    **Returns:**
    Complete film information if found.
    
    **Errors:**
    - **404**: Film with the specified ID does not exist
    - **422**: Invalid film ID format (not a positive integer)
    
    **Example Usage:**
    - Get film with ID 1: `GET /api/v1/films/1`
    """
    return await service.get_film_by_id(session, film_id)


@router.get(
    "/search/title",
    response_model=FilmListResponse,
    summary="Search Films by Title",
    description="Search for films using title keywords with case-insensitive matching",
    responses={
        200: {
            "description": "Search completed successfully",
            "model": FilmListResponse
        },
        422: {
            "description": "Invalid search parameters",
            "model": ValidationErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "detail": [
                            {
                                "type": "string_too_short",
                                "loc": ["query", "q"],
                                "msg": "String should have at least 2 characters",
                                "input": "a"
                            }
                        ]
                    }
                }
            }
        }
    }
)
async def search_films_by_title(
    q: str = Query(..., min_length=2, description="Title search term"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    session: AsyncSession = Depends(get_db_session),
    service: FilmService = Depends(get_film_service)
) -> FilmListResponse:
    """
    Search for films by title using case-insensitive partial matching.
    
    Performs a text search across film titles to find matching results. The search
    is case-insensitive and supports partial matches.
    
    **Query Parameters:**
    - **q**: Search term for film title (minimum 2 characters, required)
    - **skip**: Number of records to skip for pagination (default: 0)
    - **limit**: Maximum number of records to return (default: 10, max: 100)
    
    **Search Behavior:**
    - Case-insensitive matching
    - Partial title matches supported
    - Results ordered by relevance
    
    **Returns:**
    Paginated list of films with titles matching the search term.
    
    **Example Usage:**
    - Search for "academy": `GET /api/v1/films/search/title?q=academy`
    - Search with pagination: `GET /api/v1/films/search/title?q=action&skip=10&limit=5`
    """
    return await service.search_films_by_title(session, q, skip, limit)


@router.get(
    "/streaming/available", 
    response_model=FilmListResponse,
    summary="Get Streaming Films",
    description="Retrieve films available for streaming",
    responses={
        200: {
            "description": "Successfully retrieved streaming films",
            "model": FilmListResponse
        },
        422: {
            "description": "Validation error in query parameters",
            "model": ValidationErrorResponse
        }
    }
)
async def get_streaming_films(
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    session: AsyncSession = Depends(get_db_session),
    service: FilmService = Depends(get_film_service)
) -> FilmListResponse:
    """
    Get films available for streaming.
    
    Retrieves a paginated list of films that are available for streaming subscription.
    
    **Query Parameters:**
    - **skip**: Number of records to skip for pagination (default: 0)
    - **limit**: Maximum number of records to return (default: 10, max: 100)
    
    **Returns:**
    Paginated list of films that have streaming_available=true.
    
    **Example Usage:**
    - Get streaming films: `GET /api/v1/films/streaming/available`
    - With pagination: `GET /api/v1/films/streaming/available?skip=10&limit=20`
    """
    return await service.get_streaming_films(session, skip, limit)
