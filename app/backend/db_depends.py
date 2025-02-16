from typing import AsyncGenerator
from app.backend.db import AsyncSession
from app.backend.db import async_session_maker


async def get_db() -> AsyncGenerator[AsyncSession, None]:
    async with async_session_maker() as session:
        yield session
