from loopit.src.app import app
from fastapi.testclient import TestClient
from fastapi import status


client = TestClient(app)

def test_return_health_check():
    response = client.get("/health")
    assert response.status_code == status.HTTP_200_OK
    assert response.json() == {'status':'Healthy'} 
    

#  The AsyncMock object behaves like a coroutine function (a function defined with async def), meaning it is awaitable   