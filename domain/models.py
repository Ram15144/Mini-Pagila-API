"""SQLAlchemy database models for Pagila database."""

from datetime import datetime, date
from decimal import Decimal
from typing import Optional

from sqlalchemy import Boolean, Column, DateTime, Date, Integer, String, Numeric, ForeignKey, Text, Index
from sqlalchemy.sql import func

from domain.base import Base


class Category(Base):
    """Category model."""
    
    __tablename__ = "category"
    
    category_id = Column(Integer, primary_key=True)
    name = Column(String(25), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


class Language(Base):
    """Language model."""
    
    __tablename__ = "language"
    
    language_id = Column(Integer, primary_key=True)
    name = Column(String(20), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


class Country(Base):
    """Country model."""
    
    __tablename__ = "country"
    
    country_id = Column(Integer, primary_key=True)
    country = Column(String(50), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


class City(Base):
    """City model."""
    
    __tablename__ = "city"
    
    city_id = Column(Integer, primary_key=True)
    city = Column(String(50), nullable=False)
    country_id = Column(Integer, ForeignKey("country.country_id"), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


class Address(Base):
    """Address model."""
    
    __tablename__ = "address"
    
    address_id = Column(Integer, primary_key=True)
    address = Column(String(50), nullable=False)
    address2 = Column(String(50), nullable=True)
    district = Column(String(20), nullable=False)
    city_id = Column(Integer, ForeignKey("city.city_id"), nullable=False)
    postal_code = Column(String(10), nullable=True)
    phone = Column(String(20), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


class Store(Base):
    """Store model."""
    
    __tablename__ = "store"
    
    store_id = Column(Integer, primary_key=True)
    manager_staff_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=True)  # Made nullable to break circular dependency
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


class Staff(Base):
    """Staff model."""
    
    __tablename__ = "staff"
    
    staff_id = Column(Integer, primary_key=True)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)
    email = Column(String(50), nullable=True)
    store_id = Column(Integer, ForeignKey("store.store_id"), nullable=False)
    active = Column(Boolean, nullable=False, default=True)
    username = Column(String(16), nullable=False)
    password = Column(String(40), nullable=True)
    last_update = Column(DateTime, nullable=False, server_default=func.now())
    picture = Column(Text, nullable=True)  # bytea in postgres, but Text for simplicity


class Customer(Base):
    """Customer model."""
    
    __tablename__ = "customer"
    
    customer_id = Column(Integer, primary_key=True)
    store_id = Column(Integer, ForeignKey("store.store_id"), nullable=False)
    first_name = Column(String(45), nullable=False)
    last_name = Column(String(45), nullable=False)
    email = Column(String(50), nullable=True)
    address_id = Column(Integer, ForeignKey("address.address_id"), nullable=False)
    activebool = Column(Boolean, nullable=False, default=True)
    create_date = Column(Date, nullable=False, server_default=func.current_date())
    last_update = Column(DateTime, nullable=True, server_default=func.now())
    active = Column(Integer, nullable=True)


class Film(Base):
    """Film model with streaming_available field."""
    
    __tablename__ = "film"
    
    film_id = Column(Integer, primary_key=True)
    title = Column(String(255), nullable=False)
    description = Column(Text, nullable=True)
    release_year = Column(Integer, nullable=True)
    language_id = Column(Integer, ForeignKey("language.language_id"), nullable=False)
    rental_duration = Column(Integer, nullable=False, default=3)
    rental_rate = Column(Numeric(4, 2), nullable=False, default=Decimal("4.99"))
    length = Column(Integer, nullable=True)
    replacement_cost = Column(Numeric(5, 2), nullable=False, default=Decimal("19.99"))
    rating = Column(String(10), nullable=True, default="G")
    special_features = Column(Text, nullable=True)
    last_update = Column(DateTime, nullable=False, server_default=func.now())
    
    # streaming_available added in Migration #2
    streaming_available = Column(Boolean, nullable=False, default=False)


class Inventory(Base):
    """Inventory model."""
    
    __tablename__ = "inventory"
    
    inventory_id = Column(Integer, primary_key=True)
    film_id = Column(Integer, ForeignKey("film.film_id"), nullable=False)
    store_id = Column(Integer, ForeignKey("store.store_id"), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


class Rental(Base):
    """Rental model."""
    
    __tablename__ = "rental"
    
    rental_id = Column(Integer, primary_key=True)
    rental_date = Column(DateTime, nullable=False, server_default=func.now())
    inventory_id = Column(Integer, ForeignKey("inventory.inventory_id"), nullable=False)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    return_date = Column(DateTime, nullable=True)
    staff_id = Column(Integer, ForeignKey("staff.staff_id"), nullable=False)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


class FilmCategory(Base):
    """Film-Category many-to-many relationship."""
    
    __tablename__ = "film_category"
    
    film_id = Column(Integer, ForeignKey("film.film_id"), primary_key=True)
    category_id = Column(Integer, ForeignKey("category.category_id"), primary_key=True)
    last_update = Column(DateTime, nullable=False, server_default=func.now())


# StreamingSubscription added in Migration #3
class StreamingSubscription(Base):
    """Streaming subscription model - added in Migration #3."""
    
    __tablename__ = "streaming_subscription"
    
    id = Column(Integer, primary_key=True)
    customer_id = Column(Integer, ForeignKey("customer.customer_id"), nullable=False)
    plan_name = Column(String(100), nullable=False)
    start_date = Column(Date, nullable=False)
    end_date = Column(Date, nullable=True)
    last_update = Column(DateTime, nullable=False, server_default=func.now())