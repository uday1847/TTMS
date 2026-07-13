import logging
import time

from fastapi import Request, Response
from starlette.middleware.base import BaseHTTPMiddleware

logger = logging.getLogger("ttms.request_logger")


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """
    Middleware that records HTTP methods, request paths, status codes,
    and request process times for audit and performance monitoring.
    """

    async def dispatch(self, request: Request, call_next) -> Response:
        start_time = time.perf_counter()
        
        response = await call_next(request)
        
        process_time = (time.perf_counter() - start_time) * 1000
        formatted_process_time = f"{process_time:.2f}ms"
        
        logger.info(
            f"Method: {request.method} | Path: {request.url.path} | "
            f"Status: {response.status_code} | Duration: {formatted_process_time}"
        )
        
        return response
