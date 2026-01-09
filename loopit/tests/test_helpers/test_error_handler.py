from fastapi.responses import JSONResponse
from helpers.success_handler import write_success_response


def test_write_success_response_with_data_only():
    resp = write_success_response(
        status_code=200,
        data={"id": 1, "name": "test"},
    )

    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 200 

def test_write_success_response_with_data_and_message():
    resp = write_success_response(
        status_code=201,
        data={"id": 1},
        message="Created successfully",
    )

    assert isinstance(resp, JSONResponse)
    assert resp.status_code == 201

def test_write_success_response_with_none_data():
    resp = write_success_response(
        status_code=204,
        data=None,
    )

    assert resp.status_code == 204


def test_write_success_response_with_list_data():
    resp = write_success_response(
        status_code=200,
        data=[{"id": 1}, {"id": 2}],
    )

    assert resp.status_code == 200


def test_write_success_response_message_empty_string_ignored():
    resp = write_success_response(
        status_code=200,
        data={"ok": True},
        message="",
    )

    assert resp.status_code == 200
