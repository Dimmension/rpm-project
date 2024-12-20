# TODO: transfer to nginx
import logging
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from src.logger import logger, LOGGING_CONFIG

minio_client = Minio(
    'nginx/minio',  # Теперь MinIO доступен через Nginx
    access_key='minioadmin',
    secret_key='minioadmin',
    secure=False
)

async def upload_photo(bucket_name, object_name, photo_bytes):
    """
    Uploads a photo to MinIO directly from bytes received via Aiogram.

    Args:
        bucket_name (str): The name of the bucket in MinIO.
        object_name (str): The name of the object (file) to save in the bucket.
        photo_bytes (bytes): The photo content as bytes.
    """
    logging.config.dictConfig(LOGGING_CONFIG)
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            logger.info('Bucket with given was not found, created new one.')

        # Upload the photo as a stream
        logger.info(f'Uploading {object_name} to bucket - {bucket_name}...')
        minio_client.put_object(
            bucket_name = bucket_name,
            object_name = object_name,
            data = BytesIO(photo_bytes),
            length = len(photo_bytes),
            content_type = 'image/jpeg'  # Adjust MIME type if needed
        )
        logger.info('Upload successful!')
    except S3Error as e:
        logger.warning(f'Error occurred: {e}')
        return

async def get_photo(bucket_name, user_id):
    """
    Fetch a photo from a MinIO bucket and return the file as a BytesIO object.

    Args:
        bucket_name (str): The name of the bucket.
        object_name (str): The object name in MinIO (file name).

    Returns:
        BytesIO: The content of the photo as a BytesIO object, or None if an error occurs.
    """
    object_name = f"user_{user_id}.jpg"
    try:
        logger.info(f"Downloading {object_name} from bucket '{bucket_name}'...")
        
        response = minio_client.get_object(bucket_name=bucket_name, object_name=object_name)
        photo_file = BytesIO(response.read())
        
        response.close()
        response.release_conn()

        logger.info(f'Downloaded {object_name} from bucket {bucket_name}')
        
        return photo_file

    except S3Error as e:
        logger.warning(f'Error occurred: {e}')
        return None  # Если ошибка, возвращаем None