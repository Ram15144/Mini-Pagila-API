"""Film service for business logic operations."""

from typing import List, Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.logging import LoggingMixin, DatabaseLogger
from domain.schemas import FilmListResponse, FilmResponse, FilmQuery
from domain.models import Film
from repositories.film_repository import FilmRepository


class FilmService(LoggingMixin):
    """Service for film business logic operations."""

    def __init__(self, repository: FilmRepository):
        """Initialize film service with repository."""
        super().__init__()
        self.repository = repository
        self.logger.info("Film service initialized")

    async def list_films(
        self, 
        session: AsyncSession, 
        query: FilmQuery
    ) -> FilmListResponse:
        """
        List films with pagination and filtering.
        
        Args:
            session: Database session
            query: Film query parameters
            
        Returns:
            FilmListResponse with films and pagination info
        """
        self.log_operation_start("list_films", skip=query.skip, limit=query.limit, category=query.category)

        # Validate query parameters
        if query.skip < 0:
            self.log_validation_error("list_films", ["Skip parameter must be non-negative"], skip=query.skip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip parameter must be non-negative"
            )
        
        if query.limit <= 0 or query.limit > 100:
            self.log_validation_error("list_films", ["Limit parameter must be between 1 and 100"], limit=query.limit)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit parameter must be between 1 and 100"
            )

        # Get films from repository
        films, total = await self.repository.list_films(
            session=session,
            skip=query.skip,
            limit=query.limit,
            category=query.category
        )

        self.log_operation_success("list_films", count=len(films), total=total, category=query.category)

        # Convert to response DTOs
        film_responses = [self._film_to_response(film) for film in films]

        return FilmListResponse(
            films=film_responses,
            total=total,
            skip=query.skip,
            limit=query.limit
        )

    async def get_film_by_id(
        self, 
        session: AsyncSession, 
        film_id: int
    ) -> FilmResponse:
        """
        Get a film by its ID.
        
        Args:
            session: Database session
            film_id: Film ID to retrieve
            
        Returns:
            FilmResponse object
            
        Raises:
            HTTPException: If film not found
        """
        if film_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Film ID must be positive"
            )

        film = await self.repository.get_film_by_id(session, film_id)
        
        if not film:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Film with ID {film_id} not found"
            )

        return self._film_to_response(film)

    async def search_films_by_title(
        self,
        session: AsyncSession,
        title_search: str,
        skip: int = 0,
        limit: int = 10
    ) -> FilmListResponse:
        """
        Search films by title.
        
        Args:
            session: Database session
            title_search: Title search term
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            FilmListResponse with matching films
        """
        if not title_search or len(title_search.strip()) < 2:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Search term must be at least 2 characters long"
            )

        films, total = await self.repository.search_films_by_title(
            session=session,
            title_search=title_search.strip(),
            skip=skip,
            limit=limit
        )

        film_responses = [self._film_to_response(film) for film in films]

        return FilmListResponse(
            films=film_responses,
            total=total,
            skip=skip,
            limit=limit
        )

    async def get_streaming_films(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ) -> FilmListResponse:
        """
        Get films available for streaming.
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            FilmListResponse with streaming films
        """
        self.log_operation_start("get_streaming_films", skip=skip, limit=limit)

        # Validate parameters
        if skip < 0:
            self.log_validation_error("get_streaming_films", ["Skip parameter must be non-negative"], skip=skip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip parameter must be non-negative"
            )
        
        if limit <= 0 or limit > 100:
            self.log_validation_error("get_streaming_films", ["Limit parameter must be between 1 and 100"], limit=limit)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit parameter must be between 1 and 100"
            )

        films, total = await self.repository.get_streaming_films(
            session=session,
            skip=skip,
            limit=limit
        )
        
        self.log_operation_success("get_streaming_films", count=len(films), total=total)
        
        film_responses = [self._film_to_response(film) for film in films]
        
        return FilmListResponse(
            films=film_responses,
            total=total,
            skip=skip,
            limit=limit
        )

    def _film_to_response(self, film: Film) -> FilmResponse:
        """
        Convert Film model to FilmResponse DTO.
        
        Args:
            film: Film model instance
            
        Returns:
            FilmResponse DTO
        """
        return FilmResponse(
            film_id=film.film_id,
            title=film.title,
            description=film.description,
            release_year=film.release_year,
            rental_duration=film.rental_duration,
            rental_rate=film.rental_rate,
            length=film.length,
            rating=film.rating,
            streaming_available=film.streaming_available,
            last_update=film.last_update
        )
