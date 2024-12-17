import asyncio
import time
from neo4j import AsyncGraphDatabase, AsyncResult
from sentence_transformers import SentenceTransformer
import queries
from random import random, choice, randint


async def main():
    # driver = AsyncGraphDatabase.driver(
    #     uri='neo4j://localhost:7687',
    #     auth=('neo4j', '12345678'),
    # )
    model = SentenceTransformer('cointegrated/rubert-tiny2')
    start = time.monotonic()
    sentence = 'привет, меня зовут Егор, я люблю делать бууу'
    embedding = model.encode(sentence, normalize_embeddings=True)
    end = time.monotonic()
    print(end - start)
    # async with driver.session() as session:
    #     results: AsyncResult = await session.run(
    #         query=GET_RECOMMENDATIONS,
    #         parameters={'user_id': 1, 'top_k': 10},
    #     )
    #     recommendations = await results.data()
    #     print(len(recommendations))
    #     for recommendation in recommendations:
    #         print(recommendation)
    #         print('---' * 100)

    # async with driver.session() as session:
    #     await session.run(
    #         query=queries.CREATE_VECTOR_INDEX,
    #     )
    #     await session.run(
    #         query=queries.CREATE_AGE_INDEX,
    #     )
    #     await session.run(
    #         query=queries.CREATE_GENDER_INDEX,
    #     )

    # users = []
    # async with driver.session() as session:
    #     for i in range(50):
    #         lower_bound = choice([None, randint(1, 10)])

    #         if lower_bound is None:
    #             upper_bound = None
    #         else:
    #             upper_bound = randint(lower_bound, 45)

    #         description = choice([None, f'TestDescription{i}'])
    #         if description is None:
    #             description_embedding = None
    #         else:
    #             description_embedding = [random() for _ in range(312)]

    #         filter_by_description = choice([None, f'FilterByDescription{i}'])
    #         if filter_by_description is None:
    #             filter_by_description_embedding = None
    #         else:
    #             filter_by_description_embedding = [random() for _ in range(312)]

    #         user_data = {
    #             'user_id': i,
    #             'username': f'user_{i}',
    #             'age': randint(15, 45),
    #             'gender': choice(['masculine', 'feminine']),

    #             'description': description,
    #             'description_embedding': description_embedding,
    #             'filter_by_description': filter_by_description,
    #             'filter_by_description_embedding': filter_by_description_embedding,

    #             'filter_by_gender': choice(['masculine', 'feminine', 'all']),
    #             'filter_by_age_min': lower_bound,
    #             'filter_by_age_max': upper_bound
    #         }

    #         users.append(user_data)
    #         await session.run(
    #             query=queries.INSERT_USER,
    #             parameters=user_data,
    #         )

    # async with driver.session() as session:
    #     for user in users:
    #         parameters = {
    #             'user_id': user['user_id'],
    #             'top_k': 10
    #         }
    #         if user['filter_by_description'] or user['description']:
    #             if user['description']:
    #                 field_name = 'description_embedding'
    #             else:
    #                 field_name = 'filter_by_description_embedding'

    #             if user['filter_by_age_min']:
    #                 query = queries.GET_RECOMMENDATIONS_BY_DESCRIPTION_AND_AGE
    #                 results = await session.run(
    #                     query=query % field_name,
    #                     parameters=parameters,
    #                 )
    #             else:
    #                 query = queries.GET_RECOMMENDATIONS_BY_DESCRIPTION
    #                 results = await session.run(
    #                     query=query % field_name,
    #                     parameters=parameters,
    #                 )
    #         elif user['filter_by_age_min']:
    #             results = await session.run(
    #                 query=queries.GET_RECOMMENDATIONS_BY_AGE,
    #                 parameters=parameters,
    #             )
    #         else:
    #             results = await session.run(
    #                 query=queries.GET_RECOMMENDATIONS,
    #                 parameters=parameters
    #             )

    #         recommendations = await results.data()
    #         print(len(recommendations))

    # async with driver.session() as session:
    #     await session.run(
    #        query=queries.LIKE_USER,
    #        parameters={'user_id': 1, 'other_id': 23},
    #     )


if __name__ == '__main__':
    asyncio.run(main())
