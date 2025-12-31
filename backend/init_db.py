"""
Database initialization script.
Run this to create all tables.

Usage:
    python -m backend.init_db
"""
import asyncio
from backend.app.core.database import init_db, engine
from backend.app.models import *  # Import all models


async def main():
    """Initialize database tables."""
    print("Creating database tables...")
    await init_db()
    print("✅ Database tables created successfully!")
    
    # Close connections
    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())

