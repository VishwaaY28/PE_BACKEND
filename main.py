from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import logging

from app.database import engine, Base
from app.models import (
    Goal, Vertical, SubVertical, Capability, Process, 
    ProcessLevel, ProcessCategory, SubProcess, DataEntity, Application, API
)
from app.seed import seed_database, is_database_seeded
from app.routes import router

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI):
    """
    Lifespan context manager for application startup and shutdown.
    """
    # Startup logic
    logger.info("Starting up PE Compass API...")
    
    # Create all tables
    Base.metadata.create_all(bind=engine)
    logger.info("Database tables created successfully")
    
    # Seed database if not already seeded
    if not is_database_seeded():
        logger.info("Database not seeded. Seeding now...")
        seed_database()
        logger.info("Database seeded successfully")
    else:
        logger.info("Database already seeded, skipping seed process")
    
    yield
    
    # Shutdown logic
    logger.info("Shutting down PE Compass API...")


# Create FastAPI app
app = FastAPI(
    title="PE Compass API",
    description="Backend API for PE Compass",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins (adjust in production)
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routes
app.include_router(router)


@app.get("/")
def root():
    """Root endpoint."""
    return {
        "message": "PE Compass API",
        "version": "1.0.0",
        "endpoints": {
            "health": "/api/health",
            "all_capabilities": "/api/capabilities",
            "capability_details": "/api/capability/{capability_name}",
            "search_capabilities": "/api/capabilities/search?keyword=your_keyword",
            "docs": "/docs",
            "openapi": "/openapi.json"
        }
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
