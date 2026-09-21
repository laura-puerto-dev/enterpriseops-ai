from collections.abc import Awaitable, Callable
from uuid import uuid4

from fastapi import Request, Response

from enterpriseops_ai.observability.context import request_id_var


async def request_context_middleware(
    request: Request,
    call_next: Callable[[Request], Awaitable[Response]],
) -> Response:
    request_id = str(uuid4())
    token = request_id_var.set(request_id)

    try:
        response = await call_next(request)
        response.headers["X-Request-ID"] = request_id
        return response
    finally:
        request_id_var.reset(token)
