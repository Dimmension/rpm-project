CREATE_VECTOR_INDEX = """
CREATE VECTOR INDEX `user_description_embedding_index` IF NOT EXISTS
FOR (u:User) ON (u.description_embedding)
OPTIONS {indexConfig: {
    `vector.dimensions`: %d,
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
  user_tag: $user_tag,
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

GET_RECOMMENDATIONS = """
MATCH (current:User {user_id: $user_id})
WITH current

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
  AND (
    properties(current).filter_by_age_min IS NULL OR
    other.age >= properties(current).filter_by_age_min
  )
  AND (
    properties(current).filter_by_age_max IS NULL OR
    other.age <= properties(current).filter_by_age_max
  )

WITH current, COUNT(other) + 1 AS cnt_nodes, COLLECT(other.user_id) AS filtered_ids,
CASE
  WHEN properties(current).filter_by_description IS NOT NULL
  THEN properties(current).filter_by_description_embedding
  ELSE current.description_embedding END AS embedding

CALL db.index.vector.queryNodes(
    'user_description_embedding_index',
    cnt_nodes,
    embedding
) YIELD node, score

WHERE node.user_id IN filtered_ids
WITH node, score, CASE WHEN properties(node).description IS NOT NULL THEN 1 ELSE 0 END AS priority

RETURN
  node.user_id AS recommended_user_id,
  node.user_tag AS user_tag,
  node.username AS username,
  node.photo AS photo,
  node.gender AS gender,
  node.age AS age,
  CASE
    WHEN properties(node).description IS NOT NULL
    THEN properties(node).description ELSE NULL
  END AS description
ORDER BY priority DESC, score DESC
LIMIT $top_k;
"""

LIKE_USER = """
MATCH (u:User {user_id: $user_id})
MATCH (other:User {user_id: $other_id})
MERGE (u)-[:LIKES]->(other)
MERGE (other)-[:LIKES]->(u)
"""

GET_FULL_USER_DATA = """
MATCH (u:User {user_id: $user_id})
RETURN
  u.user_id AS user_id,
  u.user_tag AS user_tag,
  u.photo AS photo,
  u.username AS username,
  u.age AS age,
  u.gender AS gender,
  u.filter_by_gender AS filter_by_gender,
  CASE
    WHEN properties(u).description IS NOT NULL
    THEN properties(u).description ELSE NULL
  END AS description,
  CASE
    WHEN properties(u).filter_by_age_min IS NOT NULL
    THEN properties(u).filter_by_age_min ELSE NULL
  END AS filter_by_age_min,
  CASE
    WHEN properties(u).filter_by_age_max IS NOT NULL
    THEN properties(u).filter_by_age_max ELSE NULL
  END AS filter_by_age_max,
  CASE
    WHEN properties(u).filter_by_description IS NOT NULL
    THEN properties(u).filter_by_description ELSE NULL
  END AS filter_by_description;
"""

GET_FOR_LIKES_USER_DATA = """
MATCH (u:User {user_id: $user_id})
RETURN
  u.user_id AS user_id,
  u.user_tag AS user_tag,
  u.photo AS photo,
  u.username AS username,
  u.age AS age,
  u.gender AS gender,
  CASE
    WHEN properties(u).description IS NOT NULL
    THEN properties(u).description ELSE NULL
  END AS description;
"""

CHANGE_USER = """
MATCH (u:User {user_id: $user_id})
SET
  u.photo=$photo,
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

DELETE_USER = """
MATCH (u:User {user_id: $user_id}) DETACH DELETE u;
"""
