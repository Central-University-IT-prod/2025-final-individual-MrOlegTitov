from ..utils import serialize_client
from adsplatform.schemas.clients import Client
from adsplatform.db.models import Clients
from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Body, HTTPException

router = APIRouter(prefix='/clients', tags=['Clients'])


@router.get('/{client_id}')
async def get_client(client_id: UUID) -> Client:
    client = await Clients.get_or_none(id=client_id)
    if not client:
        raise HTTPException(status_code=404, detail='Client not found')

    return serialize_client(client)


@router.post('/bulk', status_code=201)
async def bulk_update(data: Annotated[list[Client], Body()]) -> list[Client]:
    result = []
    for client_data in data:
        client = await Clients.get_or_none(id=client_data.client_id)
        if (
            client_data.login
            and (not client or client.login != client_data.login)
            and await Clients.exists(login=client_data.login)
        ):
            raise HTTPException(
                status_code=409, detail=f"Login {client_data.login} already exists"
            )
        if not client:
            if (
                not client_data.login
                or client_data.age is None
                or client_data.location is None
                or not client_data.gender
            ):
                raise HTTPException(
                    status_code=400,
                    detail='You must provide all fields when creating a client',
                )
            client = await Clients.create(
                id=client_data.client_id,
                **client_data.model_dump(exclude_none=True, exclude={'client_id'}),
            )
        else:
            await client.update_from_dict(
                client_data.model_dump(exclude_none=True, exclude={'client_id'})
            )
            await client.save()

        result.append(serialize_client(client))

    return result
