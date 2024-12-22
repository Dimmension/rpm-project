from neo4j import AsyncGraphDatabase

from config.settings import settings

driver = AsyncGraphDatabase.driver(
    uri=settings.db_uri,
    auth=(settings.DB_USER, settings.DB_PASSWORD),
)
