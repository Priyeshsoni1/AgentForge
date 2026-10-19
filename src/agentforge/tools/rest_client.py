
from urllib.parse import urlsplit

import httpx

from agentforge.core.config import settings


MAX_RESPONSE_BYTES = 100_000


async def call_rest_api(
    method: str,
    url: str,
    params: dict | None = None,
    json_body: dict | None = None,
) -> dict:
    """Call an approved external HTTPS API."""

    method = method.upper()

    if method not in {"GET", "POST"}:
        raise ValueError("Only GET and POST are supported.")

    if len(url) > 2000:
        raise ValueError("URL is too long.")

    parsed = urlsplit(url)

    if (
        parsed.scheme != "https"
        or not parsed.hostname
        or parsed.username
        or parsed.password
        or parsed.port not in (None, 443)
        or parsed.hostname.endswith(".")
    ):
        raise ValueError("Only approved HTTPS URLs on port 443 are allowed.")

    hostname = parsed.hostname.lower()

    if hostname not in settings.api_host_allowlist:
        raise ValueError("URL host is not in the approved API allowlist.")

    if params and len(params) > 50:
        raise ValueError("Too many query parameters.")

    if json_body is not None and method != "POST":
        raise ValueError("JSON body is only supported for POST requests.")

    try:
        async with httpx.AsyncClient(
            timeout=10.0,
            follow_redirects=False,
            trust_env=False,
        ) as client:
            async with client.stream(
                method,
                url,
                params=params,
                json=json_body,
            ) as response:
                response.raise_for_status()

                content_length = response.headers.get("content-length")
                if content_length and int(content_length) > MAX_RESPONSE_BYTES:
                    raise ValueError("API response exceeds the size limit.")

                chunks = []
                total_bytes = 0

                async for chunk in response.aiter_bytes():
                    total_bytes += len(chunk)
                    if total_bytes > MAX_RESPONSE_BYTES:
                        raise ValueError("API response exceeds the size limit.")
                    chunks.append(chunk)

                body = b"".join(chunks).decode(
                    "utf-8", errors="replace"
                )

                return {
                    "status_code": response.status_code,
                    "content_type": response.headers.get("content-type"),
                    "body": body,
                }

    except ValueError:
        raise
    except httpx.HTTPStatusError as exc:
        raise RuntimeError(
            f"External API returned HTTP {exc.response.status_code}."
        ) from exc
    except httpx.RequestError as exc:
        raise RuntimeError("External API request failed.") from exc
