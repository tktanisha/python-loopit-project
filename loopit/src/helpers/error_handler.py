from fastapi.responses import JSONResponse


def write_error_response(status_code: int, error: str, details: str | None = None) -> JSONResponse:
    payload = {
        "status": False,
        "status_code": status_code,
        "error": error,
    }

    if details:
        payload["details"] = details

    return JSONResponse(
        status_code=status_code,
        content=payload,
    )
