from fastapi.responses import JSONResponse
from helpers.error_handler import write_error_response


def test_write_error_response_without_details():
    resp = write_error_response(
        status_code=400,
        error="Bad Request",
    )

    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 400

def test_write_error_response_with_details():
    resp = write_error_response(
        status_code=404,
        error="Not Found",
        details="Resource does not exist",
    )

    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 404

def test_write_error_response_details_empty_string_ignored():
    resp = write_error_response(
        status_code=401,
        error="Unauthorized",
        details="",
    )

    assert resp.status_code == 401