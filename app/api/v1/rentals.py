"""Rental endpoints for API version 1."""

from typing import List, Optional
from fastapi import APIRouter, Depends, Query, Path
from sqlalchemy.ext.asyncio import AsyncSession

from core.database import get_db_session
from core.auth import get_current_user
from domain.schemas import (
    RentalCreate, 
    RentalResponse, 
    ErrorResponse, 
    ValidationErrorResponse,
    UnauthorizedErrorResponse
)
from services.rental_service import RentalService
from repositories.rental_repository import RentalRepository


router = APIRouter(prefix="/customers", tags=["rentals"])

# Additional router for general rental endpoints
rentals_router = APIRouter(prefix="/rentals", tags=["rentals"])


def get_rental_repository() -> RentalRepository:
    """Get rental repository instance."""
    return RentalRepository()


def get_rental_service(
    repository: RentalRepository = Depends(get_rental_repository),
    session: AsyncSession = Depends(get_db_session)
) -> RentalService:
    """Get rental service instance."""
    return RentalService(repository, session)


@router.post(
    "/{customer_id}/rentals",
    response_model=RentalResponse,
    summary="Create New Rental",
    description="Create a new rental transaction for a customer",
    responses={
        201: {
            "description": "Rental created successfully",
            "model": RentalResponse
        },
        401: {
            "description": "Authentication required",
            "model": UnauthorizedErrorResponse
        },
        404: {
            "description": "Customer, inventory item, or staff member not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not Found",
                        "detail": "Customer with ID 999 not found or inactive",
                        "status_code": 404
                    }
                }
            }
        },
        422: {
            "description": "Validation error or business rule violation",
            "model": ValidationErrorResponse
        },
        409: {
            "description": "Inventory item already rented",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Conflict",
                        "detail": "Inventory item 123 is already rented",
                        "status_code": 409
                    }
                }
            }
        }
    },
    dependencies=[Depends(get_current_user)]
)
async def create_rental(
    customer_id: int = Path(..., gt=0, description="Customer ID"),
    *,
    rental_data: RentalCreate,
    service: RentalService = Depends(get_rental_service),
    current_user: str = Depends(get_current_user)
) -> RentalResponse:
    """
    Create a new rental transaction for a customer.
    
    **🔒 Authentication Required:** Bearer token with value `dvd_admin`
    
    Creates a new rental record linking a customer to an inventory item. The rental_date
    is automatically set to the current timestamp.
    
    **Path Parameters:**
    - **customer_id**: The ID of the customer creating the rental (must be positive)
    
    **Request Body:**
    - **inventory_id**: The ID of the inventory item to rent
    - **staff_id**: The ID of the staff member processing the rental
    
    **Business Rules:**
    - Customer must exist and be active
    - Inventory item must exist and not be currently rented
    - Staff member must exist and be active
    - All IDs must be positive integers
    
    **Returns:**
    Complete rental information including rental ID, dates, and associated IDs.
    
    **Example Usage:**
    ```
    POST /api/v1/customers/1/rentals
    Authorization: Bearer dvd_admin
    Content-Type: application/json
    
    {
        "inventory_id": 1,
        "staff_id": 1
    }
    ```
    """
    print(f"Creating rental for customer {customer_id} with data {rental_data}")
    return await service.create_rental(customer_id, rental_data)


@router.get(
    "/{customer_id}/rentals",
    response_model=List[RentalResponse],
    summary="Get Customer Rentals",
    description="Retrieve rental history for a specific customer",
    responses={
        200: {
            "description": "Customer rentals retrieved successfully",
            "model": List[RentalResponse]
        },
        404: {
            "description": "Customer not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not Found",
                        "detail": "Customer with ID 999 not found",
                        "status_code": 404
                    }
                }
            }
        },
        422: {
            "description": "Invalid customer ID or query parameters",
            "model": ValidationErrorResponse
        }
    }
)
async def get_customer_rentals(
    customer_id: int = Path(..., gt=0, description="Customer ID"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    service: RentalService = Depends(get_rental_service)
) -> List[RentalResponse]:
    """
    Retrieve rental history for a specific customer.
    
    Returns a paginated list of all rentals made by the customer, ordered by
    rental date in descending order (most recent first).
    
    **Path Parameters:**
    - **customer_id**: The ID of the customer (must be positive)
    
    **Query Parameters:**
    - **skip**: Number of records to skip for pagination (default: 0)
    - **limit**: Maximum number of records to return (default: 10, max: 100)
    
    **Returns:**
    List of rental records including both active and returned rentals.
    
    **Example Usage:**
    - Get customer 1's rentals: `GET /api/v1/customers/1/rentals`
    - Get next page: `GET /api/v1/customers/1/rentals?skip=10&limit=10`
    """
    return await service.get_customer_rentals(customer_id, skip, limit)


# Additional rental endpoints for completeness - order matters!
@rentals_router.get(
    "/active",
    response_model=List[RentalResponse],
    summary="Get Active Rentals",
    description="Retrieve all currently active rentals (not yet returned)",
    responses={
        200: {
            "description": "Active rentals retrieved successfully",
            "model": List[RentalResponse]
        },
        422: {
            "description": "Invalid query parameters",
            "model": ValidationErrorResponse
        }
    }
)
async def get_active_rentals(
    customer_id: Optional[int] = Query(None, description="Optional customer ID filter"),
    skip: int = Query(0, ge=0, description="Number of records to skip"),
    limit: int = Query(10, ge=1, le=100, description="Number of records to return"),
    service: RentalService = Depends(get_rental_service)
) -> List[RentalResponse]:
    """
    Retrieve all currently active rentals (not yet returned).
    
    Returns rentals that don't have a return_date set, optionally filtered by customer.
    Results are ordered by rental date in descending order.
    
    **Query Parameters:**
    - **customer_id**: Optional filter to show only rentals for a specific customer
    - **skip**: Number of records to skip for pagination (default: 0)
    - **limit**: Maximum number of records to return (default: 10, max: 100)
    
    **Returns:**
    List of active rental records where return_date is null.
    
    **Example Usage:**
    - Get all active rentals: `GET /api/v1/rentals/active`
    - Filter by customer: `GET /api/v1/rentals/active?customer_id=1`
    - With pagination: `GET /api/v1/rentals/active?skip=10&limit=5`
    """
    return await service.get_active_rentals(customer_id, skip, limit)


@rentals_router.get(
    "/{rental_id}",
    response_model=RentalResponse,
    summary="Get Rental by ID",
    description="Retrieve detailed information about a specific rental",
    responses={
        200: {
            "description": "Rental found and returned successfully",
            "model": RentalResponse
        },
        404: {
            "description": "Rental not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not Found",
                        "detail": "Rental with ID 999 not found",
                        "status_code": 404
                    }
                }
            }
        },
        422: {
            "description": "Invalid rental ID format",
            "model": ValidationErrorResponse
        }
    }
)
async def get_rental(
    rental_id: int = Path(..., gt=0, description="Rental ID"),
    service: RentalService = Depends(get_rental_service)
) -> RentalResponse:
    """
    Retrieve detailed information about a specific rental by its ID.
    
    Returns complete rental information including customer, inventory, staff details,
    rental and return dates.
    
    **Path Parameters:**
    - **rental_id**: The unique identifier of the rental (must be positive)
    
    **Returns:**
    Complete rental information if found.
    
    **Errors:**
    - **404**: Rental with the specified ID does not exist
    - **422**: Invalid rental ID format (not a positive integer)
    
    **Example Usage:**
    - Get rental with ID 1: `GET /api/v1/rentals/1`
    """
    return await service.get_rental_by_id(rental_id)


@rentals_router.put(
    "/{rental_id}/return",
    response_model=RentalResponse,
    summary="Return Rental",
    description="Mark a rental as returned by setting the return date",
    responses={
        200: {
            "description": "Rental returned successfully",
            "model": RentalResponse
        },
        401: {
            "description": "Authentication required",
            "model": UnauthorizedErrorResponse
        },
        404: {
            "description": "Rental not found",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Not Found",
                        "detail": "Rental with ID 999 not found",
                        "status_code": 404
                    }
                }
            }
        },
        409: {
            "description": "Rental already returned",
            "model": ErrorResponse,
            "content": {
                "application/json": {
                    "example": {
                        "error": "Conflict",
                        "detail": "Rental with ID 123 has already been returned",
                        "status_code": 409
                    }
                }
            }
        },
        422: {
            "description": "Invalid rental ID format",
            "model": ValidationErrorResponse
        }
    },
    dependencies=[Depends(get_current_user)]
)
async def return_rental(
    rental_id: int = Path(..., gt=0, description="Rental ID to return"),
    service: RentalService = Depends(get_rental_service),
    current_user: str = Depends(get_current_user)
) -> RentalResponse:
    """
    Mark a rental as returned by setting the return_date to current timestamp.
    
    **🔒 Authentication Required:** Bearer token with value `dvd_admin`
    
    Updates the rental record to set the return_date to the current timestamp and
    updates the last_update field.
    
    **Path Parameters:**
    - **rental_id**: The ID of the rental to return (must be positive)
    
    **Business Rules:**
    - Rental must exist and be currently active (not already returned)
    - Only active rentals (return_date = null) can be returned
    
    **Returns:**
    Updated rental information with return_date set.
    
    **Example Usage:**
    ```
    PUT /api/v1/rentals/1/return
    Authorization: Bearer dvd_admin
    ```
    """
    return await service.return_rental(rental_id)
