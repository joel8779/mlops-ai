from sqlalchemy import text

from app.db.session import engine


async def check_database() -> bool:
    async with engine.connect() as connection:
        await connection.execute(text("SELECT 1"))
    return True


async def close_database() -> None:
    await engine.dispose()
