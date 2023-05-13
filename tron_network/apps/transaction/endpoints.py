from typing import Union

from fastapi import APIRouter, HTTPException, status
from fastapi_utils.tasks import repeat_every

import settings
from apps.transaction import schemas
from apps.transaction.storage import TransactionStorage

router = APIRouter()
storage = TransactionStorage()


async def _create_transaction(body: schemas.BaseCreateTransactionSchema,
                              save: bool = True) -> schemas.ResponseCreateTransaction:
    obj = await storage.create(body, save=save)
    return obj.to_schema


async def _send_transaction(body: schemas.BodySendTransaction,
                            delete: bool = True) -> schemas.BaseResponseSendTransactionSchema:
    try:
        obj = storage.get(body.id, delete=delete)
        await obj.sign(private_key=body.private_key_obj)
        return await obj.send()
    except storage.TransactionNotFound as err:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=str(err),
        )


@router.on_event('startup')
@repeat_every(seconds=settings.TRANSACTION_BUFFER_CLEAR_TIME * 60)
async def clear_buffer_event():
    await storage.clear_buffer()


@router.post(
    '/transfer/create',
    response_model=schemas.ResponseCreateTransaction,
)
async def create_transfer(body: schemas.BodyCreateTransfer):
    return await _create_transaction(body)


@router.post(
    '/approve/create',
    response_model=schemas.ResponseCreateTransaction,
)
async def create_approve(body: schemas.BodyCreateApprove):
    return await _create_transaction(body)


@router.post(
    '/transfer-from/create',
    response_model=schemas.ResponseCreateTransaction,
)
async def create_transfer_from(body: schemas.BodyCreateTransferFrom):
    return await _create_transaction(body)


@router.post(
    '/freeze/create',
    response_model=schemas.ResponseCreateFreeze,
)
async def create_freeze(body: schemas.BodyFreeze):
    return await _create_transaction(body)


@router.put(
    '/transaction/send',
    response_model=Union[
        schemas.ResponseSendTransfer,
        schemas.ResponseSendApprove,
        schemas.ResponseSendTransferFrom,
    ]
)
async def send_transaction(body: schemas.BodySendTransaction):
    return await _send_transaction(body)