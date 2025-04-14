from ..config import APIConfig
from ..clients.s3 import S3ClientAsync
from ..clients.yandexgpt import YandexGPTClientAsync

import redis.asyncio as redis

api_config = APIConfig()

redis_client = redis.Redis(host='redis', port=6379)
s3_client = S3ClientAsync(
    access_key_id=api_config.minio_root_user,
    secret_access_key=api_config.minio_root_password,
    endpoint_url='http://minio:9000',
)
yandex_client = YandexGPTClientAsync(
    folder_id=api_config.yandex_folder_id, api_key=api_config.yandex_api_key
)
