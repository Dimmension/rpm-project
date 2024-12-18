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
    photo: $photo,
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
  AND (
    current.filter_by_gender = 'all' OR
    other.gender = current.filter_by_gender
  )
  AND NOT EXISTS {
    MATCH (current)-[r]->(other)
    WHERE type(r) = 'LIKES'
  }
RETURN
  other.user_id AS recommended_user_id,
  other.photo AS photo,
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
  AND (
    current.filter_by_gender = 'all' OR
    other.gender = current.filter_by_gender
  )
  AND other.age >= current.filter_by_age_min
  AND other.age <= current.filter_by_age_max
  AND NOT EXISTS {
    MATCH (current)-[r]->(other)
    WHERE type(r) = 'LIKES'
  }
RETURN
  other.user_id AS recommended_user_id,
  other.photo AS photo,
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
  AND (
    current.filter_by_gender = 'all' OR
    other.gender = current.filter_by_gender
  )
  AND other.age >= current.filter_by_age_min
  AND other.age <= current.filter_by_age_max
  AND NOT EXISTS {
    MATCH (current)-[r]->(other)
    WHERE type(r) = 'LIKES'
  }
RETURN
  other.user_id AS recommended_user_id,
  other.photo AS photo,
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
  AND (
    current.filter_by_gender = 'all' OR
    other.gender = current.filter_by_gender
  )
  AND NOT EXISTS {
    MATCH (current)-[r]->(other)
    WHERE type(r) = 'LIKES'
  }
RETURN
  other.user_id AS recommended_user_id,
  other.photo AS photo,
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

GET_USER_DATA = """
MATCH (u:User {user_id: $user_id})
RETURN
  u.user_id AS user_id,
  u.photo AS photo,
  u.username AS username,
  u.age AS age,
  u.gender AS gender,
  CASE WHEN u.description IS NOT NULL THEN u.description ELSE NULL END AS description,
  CASE WHEN u.filter_by_age_min IS NOT NULL THEN u.filter_by_age_min ELSE NULL END AS filter_by_age_min,
  CASE WHEN u.filter_by_age_max IS NOT NULL THEN u.filter_by_age_max ELSE NULL END AS filter_by_age_max,
  u.filter_by_gender AS filter_by_gender,
  CASE WHEN u.filter_by_description IS NOT NULL THEN u.filter_by_description ELSE NULL END AS filter_by_description;
"""

# TODO: change photo field
CHANGE_USER = """
MATCH (u:User {user_id: $user_id})
SET
  // u.photo=$photo,
  u.username=$username,
  u.age=$age,
  u.gender=$gender,

  u.description=$description,
  u.description_embedding=$description_embedding,

  u.filter_by_gender=$filter_by_gender,
  u.filter_by_age_min=$filter_by_age_min,
  u.filter_by_age_max=$filter_by_age_max,

  u.filter_by_description=$filter_by_description,
  u.filter_by_description_embedding=$filter_by_description_embedding
"""

