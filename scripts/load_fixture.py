import asyncio
import json
from pathlib import Path

from storage.db import driver
from consumer.handlers.form import get_user_data
from storage.queries import INSERT_USER

async def load_fixture(files: list[Path], session) -> None:
    for file in files:
        with open(file, 'r') as f:
            user_data = await get_user_data(json.load(f))
            await session.run(
                query=INSERT_USER,
                parameters=user_data,
            )

async def main(paths: list[Path]) -> None:
    await load_fixture(paths, session)  # noqa: F821
    async with driver.session() as session:
        await load_fixture(paths, session)

if __name__ == '__main__':
    asyncio.run(main(
        [
            Path('fixtures/public.user.json'),
        ]
    ))
