from .. import api_config, s3_client

from fastapi import APIRouter, HTTPException, UploadFile
from fastapi.responses import Response

router = APIRouter(prefix='/s3', tags=['S3'])


@router.get('/{file_path:path}')
async def get_file(file_path: str) -> Response:
    try:
        data, content_type = await s3_client.get_file(
            bucket=api_config.minio_bucket_name, key=file_path
        )
    except:
        raise HTTPException(status_code=404, detail='File not found')

    return Response(content=data, media_type=content_type)


@router.put('/{file_path:path}', status_code=201)
async def upload_file(file_path: str, file: UploadFile) -> None:
    await s3_client.upload_file(
        bucket=api_config.minio_bucket_name,
        key=file_path,
        data=await file.read(),
        content_type=file.content_type,
    )


@router.delete('/{file_path:path}', status_code=204)
async def delete_file(file_path: str) -> None:
    await s3_client.delete_file(
        bucket=api_config.minio_bucket_name,
        key=file_path,
    )
