CREATE_VECTOR_INDEX = """
CREATE VECTOR INDEX `user_description_embedding_index` IF NOT EXISTS
FOR (u:User) ON (u.description_embedding)
OPTIONS {indexConfig: {
    `vector.dimensions`: 312,
    `vector.similarity_function`: 'cosine'
}};
"""

CREATE_GENDER_INDEX = """
CREATE INDEX `user_gender_index` IF NOT EXISTS
FOR (u:User) ON (u.gender);
"""

CREATE_AGE_INDEX = """
CREATE INDEX `user_age_index` IF NOT EXISTS
FOR (u:User) ON (u.age);
"""

INSERT_USER = """
CREATE (u:User {
    user_id: $user_id,
    username: $username,
    age: $age,
    gender: $gender,

    description: $description,
    description_embedding: $description_embedding,

    filter_by_gender: $filter_by_gender,
    filter_by_age_min: $filter_by_age_min,
    filter_by_age_max: $filter_by_age_max,

    filter_by_description: $filter_by_description,
    filter_by_description_embedding: $filter_by_description_embedding
});
"""

GET_RECOMMENDATIONS_BY_DESCRIPTION = """
MATCH (current:User {user_id: $user_id})
CALL db.index.vector.queryNodes(
    'user_description_embedding_index',
    $top_k,
    current.%s
)
YIELD node AS other, score
WHERE other.user_id <> current.user_id
  AND other.gender = current.filter_by_gender
  AND NOT (current)-[:LIKES]->(other)
RETURN other.user_id AS recommended_user_id,
  other.username AS username,
  other.gender AS gender,
  other.age AS age,
  other.description AS description
ORDER BY score DESC
LIMIT $top_k
"""

GET_RECOMMENDATIONS_BY_DESCRIPTION_AND_AGE = """
MATCH (current:User {user_id: $user_id})
CALL db.index.vector.queryNodes(
    'user_description_embedding_index',
    $top_k,
    current.%s
)
YIELD node AS other, score
WHERE other.user_id <> current.user_id
  AND other.gender = current.filter_by_gender
  AND other.age >= current.filter_by_age_min
  AND other.age <= current.filter_by_age_max
  AND NOT (current)-[:LIKES]->(other)
RETURN other.user_id AS recommended_user_id,
  other.username AS username,
  other.gender AS gender,
  other.age AS age,
  other.description AS description
ORDER BY score DESC
LIMIT $top_k
"""

GET_RECOMMENDATIONS_BY_AGE = """
MATCH (current:User {user_id: $user_id})
MATCH (other:User)
WHERE other.user_id <> current.user_id
  AND other.gender = current.filter_by_gender
  AND other.age >= current.filter_by_age_min
  AND other.age <= current.filter_by_age_max
  AND NOT (current)-[:LIKES]->(other)
RETURN other.user_id AS recommended_user_id,
  other.username AS username,
  other.gender AS gender,
  other.age AS age,
  other.description AS description
ORDER BY rand()
LIMIT $top_k
"""

GET_RECOMMENDATIONS = """
MATCH (current:User {user_id: $user_id})
MATCH (other:User)
WHERE other.user_id <> current.user_id
  AND other.gender = current.filter_by_gender
  AND NOT (current)-[:LIKES]->(other)
RETURN other.user_id AS recommended_user_id,
  other.username AS username,
  other.gender AS gender,
  other.age AS age,
  other.description AS description
ORDER BY rand()
LIMIT $top_k
"""

LIKE_USER = """
MATCH (u:User {user_id: $user_id})
MATCH (other:User {user_id: $other_id})
MERGE (u)-[:LIKES]->(other)
MERGE (other)-[:LIKES]->(u)
"""
