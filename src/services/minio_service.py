from minio import Minio
from minio.error import S3Error
from io import BytesIO

# Initialize MinIO client
minio_client = Minio(
    #'host.docker.internal:9000'
    'minio:9000',  # Replace with your MinIO server URL
    access_key='minioadmin',
    secret_key='minioadmin',
    secure=False  # Set to False if your MinIO server doesn't use HTTPS
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
        # Ensure the bucket exists
        if not minio_client.bucket_exists(bucket_name):
            minio_client.make_bucket(bucket_name)

        # Upload the photo as a stream
        print(f"Uploading {object_name} to bucket '{bucket_name}'...")
        minio_client.put_object(
            bucket_name = bucket_name,
            object_name = object_name,
            data = BytesIO(photo_bytes),
            length = len(photo_bytes),
            content_type = 'image/jpeg'  # Adjust MIME type if needed
        )
        print('Upload successful!')
    except S3Error as e:
        print(f'Error occurred: {e}')
        return

async def get_photo(bucket_name, object_name, download_path):
    """
    Fetch a photo from a MinIO bucket and save it locally.

    Args:
        bucket_name (str): The name of the bucket.
        object_name (str): The object name in MinIO (file name).
        download_path (str): Local path to save the downloaded file.
    """
    try:
        print(f"Downloading {object_name} from bucket '{bucket_name}'...")
        # Use MinIO client to fetch the object
        minio_client.fget_object(
            bucket_name=bucket_name,
            object_name=object_name,
            file_path=download_path
        )
        print(f'Downloaded {object_name} to {download_path}')
    except S3Error as e:
        print(f'Error occurred: {e}')
