from fastapi.responses import JSONResponse
from fastapi.encoders import jsonable_encoder

def write_success_response(status_code: int, data: any = None, message: str | None = None) -> JSONResponse:
    payload = {
        "status": True,
        "data": jsonable_encoder(data)
    }

    if message:
        payload["message"] = message
    return JSONResponse(
        status_code=status_code,
        content=payload,
    )
