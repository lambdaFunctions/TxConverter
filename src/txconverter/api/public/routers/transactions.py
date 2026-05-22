from http import HTTPStatus
from typing import Annotated, Union

from fastapi import APIRouter, Depends, Query

from src.txconverter.api.common.pagination import MAX_PAGE_SIZE, PageParams
from src.txconverter.api.public.schemas.transactions import (
    PostPurchaseTransactionRequest,
    PostPurchaseTransactionResponse,
    GetTransactionListRequest,
    GetTransactionListResponse,
    GetTransactionResponse,
    GetTxConversionRequest,
    GetTxConversionResponse,
)
from src.txconverter.api.public.use_cases.transactions import (
    create_transaction,
    get_transaction_list,
    get_raw_or_converted_transaction,
)

router = APIRouter(prefix="/transactions", tags=["Transactions"])


_DEFAULT_PAGE = 1
_DEFAULT_PAGE_SIZE = 10


@router.post(
    "",
    status_code=HTTPStatus.OK,
    response_model=PostPurchaseTransactionResponse,
    responses={
        HTTPStatus.UNPROCESSABLE_ENTITY.value: {
            "description": "Invalid description length or negative amount",
        },
    },
)
async def create(body: PostPurchaseTransactionRequest):
    return await create_transaction(body)


@router.get(
    "",
    status_code=HTTPStatus.OK,
    response_model=GetTransactionListResponse,
)
async def get_list(
    filters: GetTransactionListRequest = Depends(),
    page: Annotated[int, Query(ge=1)] = _DEFAULT_PAGE,
    page_size: Annotated[int, Query(ge=1, le=MAX_PAGE_SIZE)] = _DEFAULT_PAGE_SIZE,
):
    return await get_transaction_list(
        filters, PageParams(page=page, page_size=page_size)
    )


@router.get(
    "/{id}",
    status_code=HTTPStatus.OK,
    response_model=Union[GetTransactionResponse, GetTxConversionResponse],
    responses={
        HTTPStatus.NOT_FOUND.value: {
            "description": "Transaction not found",
        },
        HTTPStatus.BAD_REQUEST.value: {
            "description": "Conversion not available, request is too old, or older than available data",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY.value: {
            "description": "Ambiguous currency — multiple matches found for the given name",
        },
        HTTPStatus.INTERNAL_SERVER_ERROR.value: {
            "description": "Error fetching currency data from external provider",
        },
    },
)
async def get_raw_or_converted(id: str, params: GetTxConversionRequest = Depends()):
    """
    If a query param for conversion is sent, the endpoint returns the current transaction
    pointed in the URL (`id`) but with the due modified response body for the action.
    """
    return await get_raw_or_converted_transaction(id, params)
