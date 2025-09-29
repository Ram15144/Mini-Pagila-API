"""Rental repository for data access operations."""

from typing import List, Optional
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select, and_
from sqlmodel import col

from domain.models import Rental, Customer, Inventory, Staff, Film


class RentalRepository:
    """Repository for rental data access operations."""

    async def create_rental(
        self,
        session: AsyncSession,
        customer_id: int,
        inventory_id: int,
        staff_id: int
    ) -> Rental:
        """
        Create a new rental record.
        
        Args:
            session: Database session
            customer_id: Customer ID creating the rental
            inventory_id: Inventory item being rented
            staff_id: Staff member processing the rental
            
        Returns:
            Created rental object
        """
        rental = Rental(
            customer_id=customer_id,
            inventory_id=inventory_id,
            staff_id=staff_id,
            rental_date=datetime.utcnow()
        )
        
        session.add(rental)
        await session.commit()
        await session.refresh(rental)
        
        return rental

    async def get_rental_by_id(
        self, 
        session: AsyncSession, 
        rental_id: int
    ) -> Optional[Rental]:
        """
        Get a rental by its ID.
        
        Args:
            session: Database session
            rental_id: Rental ID to retrieve
            
        Returns:
            Rental object if found, None otherwise
        """
        query = select(Rental).where(Rental.rental_id == rental_id)
        result = await session.execute(query)
        return result.scalars().first()

    async def get_customer_rentals(
        self, 
        session: AsyncSession, 
        customer_id: int,
        skip: int = 0,
        limit: int = 10
    ) -> List[Rental]:
        """
        Get all rentals for a specific customer.
        
        Args:
            session: Database session
            customer_id: Customer ID
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of rental objects
        """
        query = (
            select(Rental)
            .where(Rental.customer_id == customer_id)
            .order_by(Rental.rental_date.desc())
            .offset(skip)
            .limit(limit)
        )
        
        result = await session.execute(query)
        return result.scalars().all()

    async def get_active_rentals(
        self,
        session: AsyncSession,
        customer_id: Optional[int] = None,
        skip: int = 0,
        limit: int = 10
    ) -> List[Rental]:
        """
        Get active rentals (not yet returned).
        
        Args:
            session: Database session
            customer_id: Optional customer ID filter
            skip: Number of records to skip
            limit: Number of records to return
            
        Returns:
            List of active rental objects
        """
        query = select(Rental).where(Rental.return_date.is_(None))
        
        if customer_id:
            query = query.where(Rental.customer_id == customer_id)
            
        query = query.order_by(Rental.rental_date.desc()).offset(skip).limit(limit)
        
        result = await session.execute(query)
        return result.scalars().all()

    async def return_rental(
        self,
        session: AsyncSession,
        rental_id: int,
        return_date: Optional[datetime] = None
    ) -> Optional[Rental]:
        """
        Mark a rental as returned.
        
        Args:
            session: Database session
            rental_id: Rental ID to return
            return_date: Return date (defaults to current time)
            
        Returns:
            Updated rental object if found, None otherwise
        """
        rental = await self.get_rental_by_id(session, rental_id)
        
        if rental and rental.return_date is None:
            rental.return_date = return_date or datetime.utcnow()
            rental.last_update = datetime.utcnow()
            
            session.add(rental)
            await session.commit()
            await session.refresh(rental)
            
            return rental
        
        return None

    async def validate_rental_data(
        self,
        session: AsyncSession,
        customer_id: int,
        inventory_id: int,
        staff_id: int
    ) -> dict:
        """
        Validate rental data and return validation results.
        
        Args:
            session: Database session
            customer_id: Customer ID
            inventory_id: Inventory ID  
            staff_id: Staff ID
            
        Returns:
            Dictionary with validation results and related objects
        """
        validation_result = {
            "valid": True,
            "errors": [],
            "customer": None,
            "inventory": None,
            "staff": None,
            "film": None
        }

        # Check customer exists and is active
        customer_query = select(Customer).where(Customer.customer_id == customer_id)
        customer_result = await session.execute(customer_query)
        customer = customer_result.scalars().first()
        
        if not customer:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Customer with ID {customer_id} not found")
        elif not customer.activebool:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Customer with ID {customer_id} is not active")
        else:
            validation_result["customer"] = customer

        # Check inventory exists
        inventory_query = (
            select(Inventory, Film)
            .join(Film, Inventory.film_id == Film.film_id)
            .where(Inventory.inventory_id == inventory_id)
        )
        inventory_result = await session.execute(inventory_query)
        inventory_film = inventory_result.first()

        if not inventory_film:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Inventory item with ID {inventory_id} not found")
        else:
            inventory, film = inventory_film
            validation_result["inventory"] = inventory
            validation_result["film"] = film
            
            # Check if inventory item is already rented out
            active_rental_query = (
                select(Rental)
                .where(
                    and_(
                        Rental.inventory_id == inventory_id,
                        Rental.return_date.is_(None)
                    )
                )
            )
            active_rental_result = await session.execute(active_rental_query)
            active_rental = active_rental_result.scalars().first()
            
            if active_rental:
                validation_result["valid"] = False
                validation_result["errors"].append(f"Inventory item with ID {inventory_id} is already rented out")

        # Check staff exists and is active
        staff_query = select(Staff).where(Staff.staff_id == staff_id)
        staff_result = await session.execute(staff_query)
        staff = staff_result.scalars().first()
        
        if not staff:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Staff member with ID {staff_id} not found")
        elif not staff.active:
            validation_result["valid"] = False
            validation_result["errors"].append(f"Staff member with ID {staff_id} is not active")
        else:
            validation_result["staff"] = staff

        return validation_result
