from unittest.mock import patch, MagicMock
from database.connection import get_dynamodb


def test_get_dynamodb_returns_client():
    client = get_dynamodb()
    assert client is not None


def test_get_dynamodb_returns_same_instance():
    client1 = get_dynamodb()
    client2 = get_dynamodb()
    assert client1 is client2


def test_boto3_client_called_once_on_import():
    with patch("database.connection.boto3.client") as mock_client:
        mock_instance = MagicMock()
        mock_client.return_value = mock_instance

        from importlib import reload
        import database.connection as dynamodb_module
        reload(dynamodb_module)

        client = dynamodb_module.get_dynamodb()

        mock_client.assert_called_once_with("dynamodb")
        assert client is mock_instance
