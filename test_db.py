import asyncio
import ssl
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy import text  # Import text from sqlalchemy

# Your DATABASE_URL without the sslmode=require
DATABASE_URL = "postgresql+asyncpg://safezonedb_user:J5e9Xkf6i37muP9yskMzG7o9s6u4VFhH@dpg-cucs39hopnds73al2ap0-a.singapore-postgres.render.com/safezonedb"

async def test_db():
    # Create an SSLContext to enforce SSL mode
    ssl_context = ssl.create_default_context()
    ssl_context.check_hostname = False  # Disable hostname verification (if required)

    # Create engine with connect_args for SSL configuration
    engine = create_async_engine(
        DATABASE_URL, 
        echo=True, 
        connect_args={
            'ssl': ssl_context  # Pass SSL context here
        }
    )
    
    async with engine.connect() as conn:
        # Use sqlalchemy.text() for the raw SQL query
        result = await conn.execute(text("SELECT 1"))
        print(result.fetchall())  # Should return [(1,)]

# Run the async function
asyncio.run(test_db())
