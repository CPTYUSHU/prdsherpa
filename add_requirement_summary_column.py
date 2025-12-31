#!/usr/bin/env python3
"""
Add requirement_summary column to conversations table.
"""
import asyncio
from sqlalchemy import text
from backend.app.core.database import engine


async def main():
    print("Adding requirement_summary column to conversations table...")

    async with engine.begin() as conn:
        # Check if column exists
        result = await conn.execute(
            text("""
            SELECT column_name
            FROM information_schema.columns
            WHERE table_name='conversations'
            AND column_name='requirement_summary';
            """)
        )
        rows = result.fetchall()
        if len(rows) > 0:
            print("Column already exists!")
            return

        # Add column
        await conn.execute(
            text("""
            ALTER TABLE conversations
            ADD COLUMN requirement_summary JSONB NULL;
            """)
        )
        print("✅ Added requirement_summary column successfully!")

    await engine.dispose()


if __name__ == "__main__":
    asyncio.run(main())
