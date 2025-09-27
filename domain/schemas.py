"""Pydantic schemas for request/response DTOs."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional, List
from pydantic import BaseModel, Field


# Film Schemas
class FilmResponse(BaseModel):
    """Film response schema with detailed film information."""
    
    film_id: int = Field(description="Unique identifier for the film")
    title: str = Field(description="Film title")
    description: Optional[str] = Field(
        default=None, 
        description="Film description/plot summary"
    )
    release_year: Optional[int] = Field(
        default=None, 
        ge=1900,
        le=2030,
        description="Year the film was released"
    )
    rental_duration: int = Field(
        ge=1,
        le=30,
        description="Default rental duration in days"
    )
    rental_rate: Decimal = Field(
        ge=0,
        decimal_places=2,
        description="Rental cost per day"
    )
    length: Optional[int] = Field(
        default=None,
        ge=1,
        le=500,
        description="Film duration in minutes"
    )
    rating: Optional[str] = Field(
        default=None,
        pattern="^(G|PG|PG-13|R|NC-17)$",
        description="MPAA film rating"
    )
    # streaming_available: bool  # Will be added in Migration #2
    last_update: datetime = Field(description="Timestamp of last update")

    model_config = {
        "json_schema_extra": {
            "example": {
                "film_id": 1,
                "title": "Academy Dinosaur",
                "description": "An Epic Drama of a Feminist And a Mad Scientist who must Battle a Teacher in The Canadian Rockies",
                "release_year": 2006,
                "rental_duration": 6,
                "rental_rate": 0.99,
                "length": 86,
                "rating": "PG",
                "last_update": "2023-12-01T10:30:00Z"
            }
        }
    }


class FilmListResponse(BaseModel):
    """Film list response with pagination metadata."""
    
    films: List[FilmResponse] = Field(description="List of films matching the query")
    total: int = Field(ge=0, description="Total number of films available")
    skip: int = Field(ge=0, description="Number of records skipped")
    limit: int = Field(ge=1, le=100, description="Maximum number of records returned")

    model_config = {
        "json_schema_extra": {
            "example": {
                "films": [
                    {
                        "film_id": 1,
                        "title": "Academy Dinosaur",
                        "description": "An Epic Drama of a Feminist And a Mad Scientist who must Battle a Teacher in The Canadian Rockies",
                        "release_year": 2006,
                        "rental_duration": 6,
                        "rental_rate": 0.99,
                        "length": 86,
                        "rating": "PG",
                        "last_update": "2023-12-01T10:30:00Z"
                    }
                ],
                "total": 50,
                "skip": 0,
                "limit": 10
            }
        }
    }


class FilmQuery(BaseModel):
    """Film query parameters."""
    
    skip: int = Field(default=0, ge=0, description="Number of records to skip")
    limit: int = Field(default=10, ge=1, le=100, description="Number of records to return")
    category: Optional[str] = Field(default=None, description="Filter by category name")


# Rental Schemas
class RentalCreate(BaseModel):
    """Rental creation schema for new rentals."""
    
    inventory_id: int = Field(
        gt=0,
        description="ID of the inventory item to rent"
    )
    staff_id: int = Field(
        gt=0,
        description="ID of the staff member processing the rental"
    )

    model_config = {
        "json_schema_extra": {
            "example": {
                "inventory_id": 1,
                "staff_id": 1
            }
        }
    }


class RentalResponse(BaseModel):
    """Rental response schema with complete rental information."""
    
    rental_id: int = Field(description="Unique identifier for the rental")
    rental_date: datetime = Field(description="Timestamp when the rental was created")
    inventory_id: int = Field(
        gt=0,
        description="ID of the rented inventory item"
    )
    customer_id: int = Field(
        gt=0,
        description="ID of the customer who made the rental"
    )
    return_date: Optional[datetime] = Field(
        default=None,
        description="Timestamp when the rental was returned (null if still active)"
    )
    staff_id: int = Field(
        gt=0,
        description="ID of the staff member who processed the rental"
    )
    last_update: datetime = Field(description="Timestamp of last update")

    model_config = {
        "json_schema_extra": {
            "example": {
                "rental_id": 1,
                "rental_date": "2023-12-01T10:30:00Z",
                "inventory_id": 1,
                "customer_id": 1,
                "return_date": None,
                "staff_id": 1,
                "last_update": "2023-12-01T10:30:00Z"
            }
        }
    }


# Customer Schemas
class CustomerResponse(BaseModel):
    """Customer response schema."""
    
    customer_id: int
    first_name: str
    last_name: str
    email: Optional[str] = None
    active: bool


# AI Schemas
class FilmSummaryRequest(BaseModel):
    """Film summary request schema."""
    
    film_id: int = Field(description="ID of the film to summarize")


class FilmSummary(BaseModel):
    """Film summary response schema."""
    
    title: str
    rating: str
    recommended: bool


# Streaming Subscription Schemas
class StreamingSubscriptionCreate(BaseModel):
    """Streaming subscription creation schema."""
    
    customer_id: int
    plan_name: str
    start_date: date
    end_date: Optional[date] = None


class StreamingSubscriptionResponse(BaseModel):
    """Streaming subscription response schema."""
    
    id: int
    customer_id: int
    plan_name: str
    start_date: date
    end_date: Optional[date] = None


# Error Schemas
class ErrorResponse(BaseModel):
    """Standard error response schema."""
    
    error: str = Field(description="Error type or category")
    detail: Optional[str] = Field(
        default=None,
        description="Detailed error message"
    )
    status_code: int = Field(description="HTTP status code")

    model_config = {
        "json_schema_extra": {
            "example": {
                "error": "Not Found",
                "detail": "Film with ID 999 not found",
                "status_code": 404
            }
        }
    }


class ValidationErrorResponse(BaseModel):
    """Validation error response schema for 422 errors."""
    
    detail: List[dict[str, str]] = Field(description="List of validation errors")


class UnauthorizedErrorResponse(BaseModel):
    """Unauthorized error response schema for 401 errors."""
    
    detail: str = Field(description="Authentication error message")

    model_config = {
        "json_schema_extra": {
            "example": {
                "detail": "Invalid authentication credentials"
            }
        }
    }


# Health Check Schema
class HealthResponse(BaseModel):
    """Health check response schema."""
    
    status: str
    version: str
    timestamp: datetime = Field(default_factory=lambda: datetime.now())
