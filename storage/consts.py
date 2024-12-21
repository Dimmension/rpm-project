EXCHANGE_NAME = 'user_recommends'
GENERAL_USERS_QUEUE_NAME = 'user_messages'
USER_RECOMMENDATIONS_QUEUE_TEMPLATE: str = 'user_recommendations.{user_id}'
USER_LIKES_QUEUE_TEMPLATE: str = 'user_likes.{user_id}'
MIN_RECOMMENDATIONS_LIMIT: int = 5