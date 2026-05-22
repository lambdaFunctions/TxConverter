from http import HTTPStatus

from fastapi import APIRouter

from src.txconverter.api.internal.schemas.currencies import (
    PostCreateCurrencyRegisterRequest,
    PostCreateCurrencyRegisterResponse,
)
from src.txconverter.api.internal.use_cases.currencies import create_currency

router = APIRouter(prefix="/internal/currencies", tags=["Currencies"])


@router.post(
    "",
    status_code=HTTPStatus.OK,
    response_model=PostCreateCurrencyRegisterResponse,
    responses={
        HTTPStatus.NOT_FOUND.value: {
            "description": "Currency not found for the given name and date",
        },
        HTTPStatus.UNPROCESSABLE_ENTITY.value: {
            "description": "Ambiguous currency — multiple matches found for the given name",
        },
        HTTPStatus.INTERNAL_SERVER_ERROR.value: {
            "description": "Error fetching currency data from external provider",
        },
    },
)
async def create(body: PostCreateCurrencyRegisterRequest):
    return await create_currency(body)
