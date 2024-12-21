# TODO: transfer to nginx
from minio import Minio
from minio.error import S3Error
from io import BytesIO
import logging
from src.logger import LOGGING_CONFIG, logger
logging.config.dictConfig(LOGGING_CONFIG)

minio_client = Minio(
    #'host.docker.internal:9000'
    'minio:9000',
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
    try:
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)
            logger.info('Bucket with given was not found, created new one.')

        # Upload the photo as a stream
        # print(f"Uploading {object_name} to bucket '{bucket_name}'...")
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

async def get_photo(bucket_name, object_name, download_path):
    # TODO change from downloading to path, to not downloading at all
    """
    Fetch a photo from a MinIO bucket and save it locally.

    Args:
        bucket_name (str): The name of the bucket.
        object_name (str): The object name in MinIO (file name).
        download_path (str): Local path to save the downloaded file.
    """
    try:
        logger.info(f"Downloading {object_name} from bucket '{bucket_name}'...")
        # Use MinIO client to fetch the object
        minio_client.fget_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=download_path
        )
        logger.info(f'Downloaded {object_name} to {download_path}')
    except S3Error as e:
        logger.info(f'Error occurred: {e}')
