import redis
from typing import Dict, List
from config.settings import settings
import logging.config
from consumer.logger import LOGGING_CONFIG, logger
logging.config.dictConfig(LOGGING_CONFIG)

class RedisDBManager:
    def __init__(self, redis_host: str, redis_port: int):
        self.redis_host = redis_host
        self.redis_port = redis_port
        self.redis_client = redis.StrictRedis(host=self.redis_host, port=self.redis_port, decode_responses=True)
        logger.info(f"Redis({self.redis_client}) client initialized on {self.redis_host}:{self.redis_port}.")

    def add_to_collection(self, user_data: Dict):
        """Add user data to Redis collection."""
        try:
            metadata = {
                'username': str(user_data['username']),
                'age': str(user_data['age']),
                'gender': str(user_data['gender']),
                'description': str(user_data['description']),
                'filter_by_age': str(user_data['filter_by_age']),
                'filter_by_gender': str(user_data['filter_by_gender']),
                'filter_by_description': str(user_data['filter_by_description']),
            }

            user_key = f"user:{user_data['user_id']}"
            logger.info(f'Redis: {self.redis_client}')
            self.redis_client.hset(user_key, mapping=metadata)

            logger.info(f"Data for user {user_data['user_id']} added to Redis.")
        except Exception as error:
            logger.error(f"Failed to add data to Redis: {error}")
            raise error

    def add_user_like(self, user_data: dict):
        """Add a like from one user to another."""
        try:
            liker_key = f"user:{user_data['user_id']}:likes"
            self.redis_client.hset(liker_key, user_data['target_user_id'], "liked")
            logger.info(f"User {user_data['user_id']} liked user {user_data['target_user_id']}.")
        except Exception as error:
            logger.error(f"Failed to add like: {error}")
            raise error

    def check_user_likes(self, user_data: dict) -> bool:
        """Check if two users like each other and process a match."""
        try:
            liker_key = f"user:{user_data['user_id']}:likes"
            target_key = f"user:{user_data['target_user_id']}:likes"

            # Check if mutual like exists
            liker_likes = self.redis_client.hget(liker_key, user_data['target_user_id'])
            target_likes = self.redis_client.hget(target_key, user_data['user_id'])

            if liker_likes and target_likes:
                # Remove mutual likes after confirming the match
                self.redis_client.hdel(liker_key, user_data['target_user_id'])
                self.redis_client.hdel(target_key, user_data['user_id'])
                logger.info(f"Match found between user {user_data['user_id']} and user {user_data['target_user_id']}.")
                return True

            logger.info(f"No match found between user {user_data['user_id']} and user {user_data['target_user_id']}.")
            return False

        except Exception as error:
            logger.error(f"Error in check_user_likes: {error}")
            return False

    def get_recommends_by_id(self, user_id: int) -> List[Dict]:
        """
        Retrieve user metadata for potential recommendations.

        Args:
            user_id (int): The user ID for whom to find recommendations.

        Returns:
            List[Dict]: List of other users' metadata.
        """
        try:
            user_key = f"user:{user_id}"
            user_data = self.redis_client.hgetall(user_key)

            if not user_data:
                logger.warning(f"No metadata found for user {user_id}.")
                return []

            # Fetch all users
            similar_users = []
            for key in self.redis_client.scan_iter(match="user:*"):
                if key == user_key:
                    continue
                other_data = self.redis_client.hgetall(key)
                similar_users.append(other_data)

            logger.info(f"Potential recommendations for user {user_id}: {similar_users}")
            return similar_users

        except Exception as error:
            logger.error(f"Error in get_recommends_by_id: {error}")
            return []

    def close_client(self):
        """Close the Redis client connection."""
        logger.info("Redis client connection closed.")

redis_manager = RedisDBManager(
    settings.REDIS_HOST, 6379
)