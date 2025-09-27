"""Rental service for business logic operations."""

from typing import List
from sqlalchemy.ext.asyncio import AsyncSession
from fastapi import HTTPException, status

from core.logging import LoggingMixin
from domain.schemas import RentalCreate, RentalResponse
from domain.models import Rental
from repositories.rental_repository import RentalRepository


class RentalService(LoggingMixin):
    """Service for rental business logic operations."""

    def __init__(self, repository: RentalRepository):
        """Initialize rental service with repository."""
        super().__init__()
        self.repository = repository
        self.logger.info("Rental service initialized")

    async def create_rental(
        self,
        session: AsyncSession,
        customer_id: int,
        rental_data: RentalCreate
    ) -> RentalResponse:
        """
        Create a new rental with business logic validation.
        
        Args:
            session: Database session
            customer_id: Customer ID from URL path
            rental_data: Rental creation data
            
        Returns:
            RentalResponse object
            
        Raises:
            HTTPException: For validation errors or business rule violations
        """
        # Validate input parameters
        if customer_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID must be positive"
            )

        if rental_data.inventory_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Inventory ID must be positive"
            )

        if rental_data.staff_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Staff ID must be positive"
            )

        # Validate rental data using repository
        validation_result = await self.repository.validate_rental_data(
            session=session,
            customer_id=customer_id,
            inventory_id=rental_data.inventory_id,
            staff_id=rental_data.staff_id
        )

        if not validation_result["valid"]:
            # Return detailed validation errors
            error_details = "; ".join(validation_result["errors"])
            raise HTTPException(
                status_code=status.HTTP_422_UNPROCESSABLE_ENTITY,
                detail=f"Rental validation failed: {error_details}"
            )

        try:
            # Create the rental
            rental = await self.repository.create_rental(
                session=session,
                customer_id=customer_id,
                inventory_id=rental_data.inventory_id,
                staff_id=rental_data.staff_id
            )

            return self._rental_to_response(rental)

        except Exception as e:
            # Handle database errors
            raise HTTPException(
                status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
                detail=f"Failed to create rental: {str(e)}"
            )

    async def get_rental_by_id(
        self,
        session: AsyncSession,
        rental_id: int
    ) -> RentalResponse:
        """
        Get a rental by its ID.
        
        Args:
            session: Database session
            rental_id: Rental ID to retrieve
            
        Returns:
            RentalResponse object
            
        Raises:
            HTTPException: If rental not found or invalid ID
        """
        if rental_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rental ID must be positive"
            )

        rental = await self.repository.get_rental_by_id(session, rental_id)
        
        if not rental:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Rental with ID {rental_id} not found"
            )

        return self._rental_to_response(rental)

    async def get_customer_rentals(
        self,
        session: AsyncSession,
        customer_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[RentalResponse]:
        """
        Get all rentals for a specific customer.
        
        Args:
            session: Database session
            customer_id: Customer ID
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of RentalResponse objects
        """
        if customer_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID must be positive"
            )

        if skip < 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Skip parameter must be non-negative"
            )

        if limit <= 0 or limit > 100:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Limit parameter must be between 1 and 100"
            )

        rentals = await self.repository.get_customer_rentals(
            session=session,
            customer_id=customer_id,
            skip=skip,
            limit=limit
        )

        return [self._rental_to_response(rental) for rental in rentals]

    async def get_active_rentals(
        self,
        session: AsyncSession,
        customer_id: int = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[RentalResponse]:
        """
        Get active rentals (not yet returned).
        
        Args:
            session: Database session
            customer_id: Optional customer ID filter
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of active RentalResponse objects
        """
        if customer_id is not None and customer_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Customer ID must be positive"
            )

        rentals = await self.repository.get_active_rentals(
            session=session,
            customer_id=customer_id,
            skip=skip,
            limit=limit
        )

        return [self._rental_to_response(rental) for rental in rentals]

    async def return_rental(
        self,
        session: AsyncSession,
        rental_id: int
    ) -> RentalResponse:
        """
        Return a rental.
        
        Args:
            session: Database session
            rental_id: Rental ID to return
            
        Returns:
            Updated RentalResponse object
            
        Raises:
            HTTPException: If rental not found or already returned
        """
        if rental_id <= 0:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail="Rental ID must be positive"
            )

        rental = await self.repository.return_rental(session, rental_id)
        
        if not rental:
            # Check if rental exists but is already returned
            existing_rental = await self.repository.get_rental_by_id(session, rental_id)
            if existing_rental:
                if existing_rental.return_date:
                    raise HTTPException(
                        status_code=status.HTTP_400_BAD_REQUEST,
                        detail=f"Rental with ID {rental_id} has already been returned"
                    )
            
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail=f"Active rental with ID {rental_id} not found"
            )

        return self._rental_to_response(rental)

    def _rental_to_response(self, rental: Rental) -> RentalResponse:
        """
        Convert Rental model to RentalResponse DTO.
        
        Args:
            rental: Rental model instance
            
        Returns:
            RentalResponse DTO
        """
        return RentalResponse(
            rental_id=rental.rental_id,
            rental_date=rental.rental_date,
            inventory_id=rental.inventory_id,
            customer_id=rental.customer_id,
            return_date=rental.return_date,
            staff_id=rental.staff_id,
            last_update=rental.last_update
        )
