"""Film service for business logic operations."""

from decimal import Decimal
from datetime import datetime
from typing import Optional
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status
from semantic_kernel.functions import kernel_function
from core.logging import LoggingMixin
from domain.schemas import FilmListResponse, FilmResponse, FilmQuery
from domain.models import Film
from repositories.film_repository import FilmRepository



class FilmService(LoggingMixin):
    """Service for film business logic operations."""

    def __init__(self, repository: FilmRepository, session: AsyncSession):
        """Initialize film service with repository."""
        super().__init__()
        self.repository = repository
        self.session = session
        self.logger.info("Film service initialized")

    @kernel_function(
        description="List films with pagination and filtering",
        name="list_films"
    )
    async def list_films(
        self, 
        skip: int,
        limit: int,
        category: Optional[str] = None
    ) -> FilmListResponse:
        """
        List films with pagination and filtering.
        
        Args:
            skip: Number of records to skip
            limit: Number of records to return
            category: Optional category name filter
            
        Returns:
            FilmListResponse with films and pagination info
        """
        
        self.log_operation_start("list_films", skip=skip, limit=limit, category=category)

        # Validate query parameters
        if skip < 0:
            self.log_validation_error("list_films", ["Skip parameter must be non-negative"], skip=skip)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip parameter must be non-negative"
            )
        
        if limit <= 0 or limit > 100:
            self.log_validation_error("list_films", ["Limit parameter must be between 1 and 100"], limit=limit)
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit parameter must be between 1 and 100"
            )

        # Get films from repository
        films, total = await self.repository.list_films(
            session=self.session,
            skip=skip,
            limit=limit,
            category=category
        )   

        self.log_operation_success("list_films", count=len(films), total=total, category=category)

        # Convert to response DTOs
        film_responses = [self.film_to_response(film) for film in films]

        return FilmListResponse(
            films=film_responses,
            total=total,
            skip=skip,
            limit=limit
        )

    @kernel_function(
        description="Get detailed information about a specific film by ID",
        name="get_film_by_id"
    )
    async def get_film_by_id(
        self, 
        film_id: int
    ) -> FilmResponse:
        """
        Get a film by its ID.
        
        Args:
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

        film = await self.repository.get_film_by_id(self.session, film_id)
        
        if not film:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Film with ID {film_id} not found"
            )

        return self.film_to_response(film)

    @kernel_function(
        description="Search for films by title and return detailed information",
        name="search_films_by_title"
    )
    async def search_films_by_title(
        self,
        title_search: str,
        skip: int = 0,
        limit: int = 10,
    ) -> FilmListResponse:
        """
        Search films by title.
        
        Args:
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
            session=self.session,
            title_search=title_search.strip(),
            skip=skip,
            limit=limit
        )

        film_responses = [self.film_to_response(film) for film in films]

        return FilmListResponse(
            films=film_responses,
            total=total,
            skip=skip,
            limit=limit
        )

    @kernel_function(
        description="Get list of films available for streaming",
        name="get_streaming_films"
    )
    async def get_streaming_films(
        self,
        skip: int = 0,
        limit: int = 10,
    ) -> FilmListResponse:
        """
        Get films available for streaming.
        
        Args:
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
            session=self.session,
            skip=skip,
            limit=limit
        )
        
        self.log_operation_success("get_streaming_films", count=len(films), total=total)
        
        film_responses = [self.film_to_response(film) for film in films]
        
        return FilmListResponse(
            films=film_responses,
            total=total,
            skip=skip,
            limit=limit
        )

    def film_to_response(self, film: Film) -> FilmResponse:
        """
        Convert Film model to FilmResponse DTO.
        
        Args:
            film: Film model instance
            
        Returns:
            FilmResponse DTO
        """
        return FilmResponse(
            film_id=int(getattr(film, "film_id", -1)), # film.film_id,
            title=str(film.title),
            description=str(film.description),
            release_year=int(getattr(film, "release_year", 0)), # film.release_year,
            rental_duration= int(getattr(film, "rental_duration", 0)), # film.rental_duration,
            rental_rate=Decimal(getattr(film, "rental_rate", 0)).quantize(Decimal('0.01')), # film.rental_rate,
            length=int(getattr(film, "length", 0)),
            rating=str(film.rating),
            streaming_available=bool(getattr(film, "streaming_available", False)),
            last_update=getattr(film, "last_update", datetime.min)
        )
