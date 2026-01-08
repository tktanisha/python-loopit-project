from fastapi import Request 

def override_verify_jwt(request:Request,role:str):
    request.state.user={
        "user_id":"1",
        "role":role
    }

