import asyncio
import json
from pathlib import Path

from storage.db import driver
from neo4j import AsyncSession

from storage.queries import INSERT_USER


async def load_fixture(files: list[Path], session: AsyncSession) -> None:
    for file in files:
        with open(file, 'r') as f:
            users = json.load(f)
            for user in users:
                await session.run(
                    query=INSERT_USER,
                    parameters=user,
                )


async def main(paths: list[Path]) -> None:
    async with driver.session() as session:
        await load_fixture(paths, session)


if __name__ == '__main__':
    asyncio.run(main(
        [
            Path('fixtures/users.json'),
        ]
    ))
