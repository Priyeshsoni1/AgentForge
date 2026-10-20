
import logging
import time
import uuid
from contextvars import ContextVar

from starlette.middleware.base import BaseHTTPMiddleware
from starlette.requests import Request
from starlette.responses import Response


request_id_var: ContextVar[str] = ContextVar(
    "request_id",
    default="-",
)


class RequestIdFilter(logging.Filter):
    """Add the current request ID to each log record."""

    def filter(self, record: logging.LogRecord) -> bool:
        record.request_id = request_id_var.get()
        return True


def configure_logging() -> None:
    """Configure consistent application log formatting."""
    handler = logging.StreamHandler()
    handler.setFormatter(
        logging.Formatter(
            "%(asctime)s %(levelname)s "
            "request_id=%(request_id)s "
            "%(name)s: %(message)s"
        )
    )
    handler.addFilter(RequestIdFilter())

    root = logging.getLogger()
    root.handlers.clear()
    root.addHandler(handler)
    root.setLevel(logging.INFO)


class RequestLoggingMiddleware(BaseHTTPMiddleware):
    """Log request duration and attach a request ID to responses."""

    async def dispatch(
        self,
        request: Request,
        call_next,
    ) -> Response:
        supplied_id = request.headers.get("X-Request-ID", "")
        # Accept only simple, bounded IDs from callers.
        if (
            supplied_id
            and len(supplied_id) <= 64
            and all(c.isalnum() or c in "-_" for c in supplied_id)
        ):
            request_id = supplied_id
        else:
            request_id = uuid.uuid4().hex

        token = request_id_var.set(request_id)
        started = time.perf_counter()

        try:
            response = await call_next(request)
            duration_ms = (time.perf_counter() - started) * 1000
            response.headers["X-Request-ID"] = request_id

            logging.getLogger("agentforge.http").info(
                "%s %s status=%s duration_ms=%.2f",
                request.method,
                request.url.path,
                response.status_code,
                duration_ms,
            )
            return response
        except Exception:
            duration_ms = (time.perf_counter() - started) * 1000
            logging.getLogger("agentforge.http").exception(
                "%s %s failed duration_ms=%.2f",
                request.method,
                request.url.path,
                duration_ms,
            )
            raise
        finally:
            request_id_var.reset(token)
