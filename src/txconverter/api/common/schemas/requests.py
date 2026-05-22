from typing import Optional

from pydantic import BaseModel


class PagingParams(BaseModel):
    """We don't need to validate max/min inputs given that
    the functions that handle the request will do it.
    """

    page: Optional[int] = None
    page_size: Optional[int] = None
