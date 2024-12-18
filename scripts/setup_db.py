import asyncio
from storage.db import driver
from storage.queries import (
    CREATE_AGE_INDEX,
    CREATE_GENDER_INDEX,
    CREATE_VECTOR_INDEX
)


async def main():
    async with driver.session() as session:
        await session.run(CREATE_VECTOR_INDEX)
        await session.run(CREATE_AGE_INDEX)
        await session.run(CREATE_GENDER_INDEX)


if __name__ == '__main__':
    asyncio.run(main())
