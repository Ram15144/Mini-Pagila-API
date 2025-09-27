"""Film repository for data access operations."""

from typing import List, Optional, Tuple
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, func, and_
from sqlmodel import col

from core.logging import LoggingMixin, DatabaseLogger
from domain.models import Film, Category, FilmCategory


class FilmRepository(LoggingMixin):
    """Repository for film data access operations."""
    
    def __init__(self):
        """Initialize film repository."""
        super().__init__()
        self.logger.info("Film repository initialized")

    async def list_films(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10,
        category: Optional[str] = None
    ) -> Tuple[List[Film], int]:
        """
        List films with pagination and optional category filtering.
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Number of records to return
            category: Optional category name filter
            
        Returns:
            Tuple of (films list, total count)
        """
        # Base query
        query = select(Film)
        count_query = select(func.count(Film.film_id))
        
        # Add category filter if provided
        if category:
            # Join with film_category and category tables
            query = query.join(FilmCategory, Film.film_id == FilmCategory.film_id)
            query = query.join(Category, FilmCategory.category_id == Category.category_id)
            query = query.where(Category.name.ilike(f"%{category}%"))
            
            # Apply same filter to count query
            count_query = count_query.join(FilmCategory, Film.film_id == FilmCategory.film_id)
            count_query = count_query.join(Category, FilmCategory.category_id == Category.category_id)
            count_query = count_query.where(Category.name.ilike(f"%{category}%"))
        
        # Apply pagination to main query
        query = query.offset(skip).limit(limit)
        query = query.order_by(Film.title)  # Order by title for consistent results
        
        DatabaseLogger.log_query("list_films", "film", skip=skip, limit=limit, category=category)

        # Execute queries
        films_result = await session.execute(query)
        films = films_result.scalars().all()
        
        count_result = await session.execute(count_query)
        total = count_result.scalar_one()
        
        DatabaseLogger.log_query_result("list_films", result_count=len(films), total=total)
        
        return films, total

    async def get_film_by_id(self, session: AsyncSession, film_id: int) -> Optional[Film]:
        """
        Get a film by its ID.
        
        Args:
            session: Database session
            film_id: Film ID to retrieve
            
        Returns:
            Film object if found, None otherwise
        """
        query = select(Film).where(Film.film_id == film_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_films_by_category(
        self, 
        session: AsyncSession, 
        category_name: str,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Film], int]:
        """
        Get films by category name with pagination.
        
        Args:
            session: Database session
            category_name: Name of the category
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            Tuple of (films list, total count)
        """
        return await self.list_films(session, skip, limit, category_name)

    async def search_films_by_title(
        self,
        session: AsyncSession,
        title_search: str,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Film], int]:
        """
        Search films by title with pagination.
        
        Args:
            session: Database session
            title_search: Title search term
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            Tuple of (films list, total count)
        """
        # Query with title search
        query = select(Film).where(Film.title.ilike(f"%{title_search}%"))
        count_query = select(func.count(Film.film_id)).where(Film.title.ilike(f"%{title_search}%"))
        
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Film.title)
        
        # Execute queries
        films_result = await session.execute(query)
        films = films_result.scalars().all()
        
        count_result = await session.execute(count_query)
        total = count_result.scalar_one()
        
        return films, total

    async def get_streaming_films(
        self,
        session: AsyncSession,
        skip: int = 0,
        limit: int = 10
    ) -> Tuple[List[Film], int]:
        """
        Get films that are available for streaming.
        
        Args:
            session: Database session
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            Tuple of (films list, total count)
        """
        # Query for streaming available films
        query = select(Film).where(Film.streaming_available == True)
        count_query = select(func.count(Film.film_id)).where(Film.streaming_available == True)
        
        # Apply pagination and ordering
        query = query.offset(skip).limit(limit).order_by(Film.title)
        
        DatabaseLogger.log_query("get_streaming_films", "film", skip=skip, limit=limit)
        
        # Execute queries
        films_result = await session.execute(query)
        films = films_result.scalars().all()
        
        count_result = await session.execute(count_query)
        total = count_result.scalar_one()
        
        DatabaseLogger.log_query_result("get_streaming_films", result_count=len(films), total=total)
        
        return films, total
