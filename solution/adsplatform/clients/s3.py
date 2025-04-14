from aiobotocore.session import AioSession


class S3ClientAsync:
    def __init__(
        self, access_key_id: str, secret_access_key: str, endpoint_url: str
    ) -> None:
        self.__access_key_id = access_key_id
        self.__secret_access_key = secret_access_key
        self.endpoint_url = endpoint_url

        self._session = AioSession()

    async def upload_file(
        self, bucket: str, key: str, data: bytes, content_type: str | None = None
    ) -> None:
        async with self._session.create_client(
            service_name='s3',
            aws_access_key_id=self.__access_key_id,
            aws_secret_access_key=self.__secret_access_key,
            endpoint_url=self.endpoint_url,
        ) as s3_client:
            await s3_client.put_object(
                Bucket=bucket,
                Key=key,
                Body=data,
                ContentType=content_type,
            )

    async def get_file(self, bucket: str, key: str) -> tuple[bytes, str | None]:
        async with self._session.create_client(
            service_name='s3',
            aws_access_key_id=self.__access_key_id,
            aws_secret_access_key=self.__secret_access_key,
            endpoint_url=self.endpoint_url,
        ) as s3_client:
            resp = await s3_client.get_object(Bucket=bucket, Key=key)
            async with resp['Body'] as stream:
                return await stream.read(), resp['ContentType']

    async def delete_file(self, bucket: str, key: str) -> None:
        async with self._session.create_client(
            service_name='s3',
            aws_access_key_id=self.__access_key_id,
            aws_secret_access_key=self.__secret_access_key,
            endpoint_url=self.endpoint_url,
        ) as s3_client:
            await s3_client.delete_object(Bucket=bucket, Key=key)

    async def key_exists(self, bucket: str, key: str) -> bool:
        async with self._session.create_client(
            service_name='s3',
            aws_access_key_id=self.__access_key_id,
            aws_secret_access_key=self.__secret_access_key,
            endpoint_url=self.endpoint_url,
        ) as s3_client:
            try:
                await s3_client.head_object(Bucket=bucket, Key=key)
                return True
            except:
                return False
