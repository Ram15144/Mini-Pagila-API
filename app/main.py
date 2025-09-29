"""FastAPI application main module."""

from contextlib import asynccontextmanager
import time
from fastapi import FastAPI, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
# from fastapi.security import HTTPBearer  # Will be used for OpenAPI schema

from core.config import settings
from core.database import close_db
from core.auth import get_current_user
from core.logging import configure_logging, app_logger, set_correlation_id
from app.api.v1.films import router as films_router
from app.api.v1.rentals import router as rentals_router, rentals_router as rentals_general_router
from app.api.v1.ai import router as ai_router
# from app.agents.orchestration import HandoffOrchestrationService


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager."""
    # Startup
    configure_logging()
    app_logger.info("🚀 Starting Pagila API...", version="0.1.0", environment="development" if settings.debug else "production")
    yield
    # Shutdown
    app_logger.info("🛑 Shutting down Pagila API...")
    await close_db()


def create_app() -> FastAPI:
    """Create and configure FastAPI application."""
    app = FastAPI(
        title="Pagila API",
        description="""
        ## Mini Pagila API with Gen AI capabilities
        
        A comprehensive DVD rental management system API built with FastAPI, featuring:
        
        * **Film Management**: Browse, search, and discover films in the catalog
        * **Rental Operations**: Handle customer rentals and returns with business logic validation
        * **Authentication**: Secure endpoints with Bearer token authentication
        * **Streaming Features**: Future streaming subscription management (Migration #2)
        
        ### Authentication
        
        Protected endpoints require Bearer token authentication with the value `dvd_admin`.
        
        ### API Versioning
        
        This API uses path-based versioning with `/api/v1/` prefix for all endpoints.
        """,
        version="0.1.0",
        debug=settings.debug,
        docs_url="/docs",
        redoc_url="/redoc",
        openapi_url="/openapi.json",
        lifespan=lifespan,
        contact={
            "name": "Pagila API Support",
            "email": "support@pagila-api.com",
        },
        license_info={
            "name": "MIT License",
            "url": "https://opensource.org/licenses/MIT",
        },
        servers=[
            {
                "url": "http://localhost:8000",
                "description": "Development server"
            }
        ],
        tags_metadata=[
            {
                "name": "health",
                "description": "Health check and system status endpoints"
            },
            {
                "name": "authentication",
                "description": "Authentication and protected endpoints for testing"
            },
            {
                "name": "films",
                "description": "Film catalog management - browse, search, and discover films"
            },
             {
                 "name": "rentals",
                 "description": "Rental operations - create rentals, manage returns, and track customer history"
             },
             {
                 "name": "ai",
                 "description": "AI-powered features using Semantic Kernel - chat assistance and film recommendations"
             }
        ]
    )
    
    # Configure OpenAPI security scheme (will be used in openapi schema)
    
    # Add security scheme to OpenAPI
    if hasattr(app, 'openapi_schema') and app.openapi_schema:
        app.openapi_schema["components"]["securitySchemes"] = {
            "bearerAuth": {
                "type": "http",
                "scheme": "bearer",
                "bearerFormat": "string",
                "description": "Enter 'dvd_admin' as the bearer token"
            }
        }
    else:
        # Will be set when OpenAPI schema is generated
        def custom_openapi():
            if app.openapi_schema:
                return app.openapi_schema
            
            from fastapi.openapi.utils import get_openapi
            openapi_schema = get_openapi(
                title=app.title,
                version=app.version,
                description=app.description,
                routes=app.routes,
            )
            
            openapi_schema["components"]["securitySchemes"] = {
                "bearerAuth": {
                    "type": "http",
                    "scheme": "bearer",
                    "bearerFormat": "string",
                    "description": "Enter 'dvd_admin' as the bearer token"
                }
            }
            
            app.openapi_schema = openapi_schema
            return app.openapi_schema
        
        app.openapi = custom_openapi
    
    # Add request logging middleware
    @app.middleware("http")
    async def logging_middleware(request: Request, call_next):
        """Log all HTTP requests and responses."""
        # Set correlation ID for this request
        correlation_id = set_correlation_id()
        
        # Start timing
        start_time = time.time()
        
        # Log request
        app_logger.info(
            "Request started",
            method=request.method,
            path=request.url.path,
            query_params=dict(request.query_params),
            correlation_id=correlation_id,
            client_ip=request.client.host if request.client else None
        )
        
        # Process request
        try:
            response = await call_next(request)
            
            # Calculate duration
            duration_ms = (time.time() - start_time) * 1000
            
            # Log response
            app_logger.info(
                "Request completed",
                method=request.method,
                path=request.url.path,
                status_code=response.status_code,
                duration_ms=round(duration_ms, 2),
                correlation_id=correlation_id
            )
            
            # Add correlation ID to response headers
            response.headers["X-Correlation-ID"] = correlation_id
            
            return response
            
        except Exception as e:
            # Calculate duration for error case
            duration_ms = (time.time() - start_time) * 1000
            
            # Log error
            app_logger.error(
                "Request failed",
                method=request.method,
                path=request.url.path,
                duration_ms=round(duration_ms, 2),
                error_type=type(e).__name__,
                error_message=str(e),
                correlation_id=correlation_id
            )
            raise

    # Add CORS middleware
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],  # Configure appropriately for production
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    
    # Health check endpoint
    @app.get(
        "/health", 
        response_model=dict,
        tags=["health"],
        summary="Health Check",
        description="Check the health status of the API service",
        responses={
            200: {
                "description": "Service is healthy",
                "content": {
                    "application/json": {
                        "example": {
                            "status": "healthy",
                            "version": "0.1.0"
                        }
                    }
                }
            }
        }
    )
    async def health_check():
        """
        Health check endpoint to verify service availability.
        
        Returns the current status and version of the API service.
        This endpoint is typically used by load balancers and monitoring systems.
        """
        return {"status": "healthy", "version": "0.1.0"}
    
    # Protected test endpoint
    @app.get(
        "/protected", 
        response_model=dict,
        tags=["authentication"],
        summary="Protected Endpoint Test",
        description="Test endpoint that requires Bearer token authentication",
        responses={
            200: {
                "description": "Authentication successful",
                "content": {
                    "application/json": {
                        "example": {
                            "message": "Access granted",
                            "user": "dvd_admin"
                        }
                    }
                }
            },
            401: {
                "description": "Authentication failed",
                "content": {
                    "application/json": {
                        "example": {
                            "detail": "Invalid authentication credentials"
                        }
                    }
                }
            }
        },
        dependencies=[Depends(get_current_user)]
    )
    async def protected_endpoint(user: str = Depends(get_current_user)):
        """
        Protected endpoint that requires authentication.
        
        This endpoint demonstrates the authentication mechanism used throughout the API.
        Requires a Bearer token with the value 'dvd_admin'.
        
        **Authentication:**
        - Header: `Authorization: Bearer dvd_admin`
        """
        return {"message": "Access granted", "user": user}
    
    # Include API routers
    app.include_router(films_router, prefix="/api/v1")
    app.include_router(rentals_router, prefix="/api/v1")
    app.include_router(rentals_general_router, prefix="/api/v1")
    app.include_router(ai_router, prefix="/api/v1")
    
    return app


# Create the FastAPI application instance
app = create_app()
