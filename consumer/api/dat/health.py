from starlette.requests import Request
from starlette.responses import Response

from .router import router


@router.get("/health")
async def health(request: Request) -> Response:
    return Response(status_code=200)