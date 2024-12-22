import logging
from config.settings import settings
from minio import Minio
from minio.error import S3Error
from io import BytesIO
from src.logger import logger, LOGGING_CONFIG
from aiogram.types import BufferedInputFile
# Initialize the Minio client correctly
minio_client = Minio(
    f'nginx:{settings.NGINX_PORT}',  # Updated to point to Nginx as the proxy to MinIO
    access_key=settings.MINIO_USERNAME,
    secret_key=settings.MINIO_PASSWORD,
    secure=False  # Change to True if Nginx proxies MinIO over HTTPS
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
            logger.info(f'Bucket "{bucket_name}" was not found; created a new one.')

        # Upload the photo as a stream
        logger.info(f'Uploading {object_name} to bucket - {bucket_name}...')
        minio_client.put_object(
            bucket_name=bucket_name,
            object_name=object_name,
            data=BytesIO(photo_bytes),
            length=len(photo_bytes),
            content_type='image/jpeg'  # Adjust MIME type if needed
        )
        logger.info('Upload successful!')
    except S3Error as e:
        logger.warning(f'Error occurred during upload: {e}')

async def get_photo(bucket_name: str, user_id: str) -> BufferedInputFile | None:
    """
    Fetch a photo from a MinIO bucket and return the file as a BufferedInputFile.

    Args:
        bucket_name (str): The name of the bucket.
        user_id (str): The ID of the user (used to construct the object name).

    Returns:
        BufferedInputFile | None: The photo file or None if an error occurs.
    """
    object_name = f"user_{user_id}.jpg"
    try:
        logger.info(f"Downloading \"{object_name}\" from bucket \"{bucket_name}\"...")

        response = minio_client.get_object(bucket_name=bucket_name, object_name=object_name)
        photo_file = BytesIO(response.read())

        response.close()
        response.release_conn()

        photo_file.seek(0)

        logger.info(f'Download of "{object_name}" from bucket "{bucket_name}" successful.')

        return BufferedInputFile(photo_file.read(), filename=object_name)

    except S3Error as e:
        logger.warning(f'Error occurred during download of "{object_name}": {e}')
    except Exception as e:
        logger.error(f'Unexpected error during download: {e}')
    return None