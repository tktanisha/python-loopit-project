
from dotenv import load_dotenv
load_dotenv()
from fastapi import FastAPI
# from api.v1.routes.auth import router as auth_router
from api.v1.routes.category import router as category_router
# from api.v1.routes.society import router as society_router
# from api.v1.routes.product import router as product_router
# from api.v1.routes.order import router as order_router
# from api.v1.routes.buy_request import router as buy_request_router
# from api.v1.routes.return_request import router as return_request_router
# from api.v1.routes.feedback import router as feedback_router
# from api.v1.routes.user import router as user_router


app = FastAPI(
    title="Loopit",
    summary="""
        A FastApi based Neighbourhood exchange application
    """,
    version="v1",
)

@app.get("/health")
def health():
    return{
        'status':'Healthy'
    }

# app.include_router(auth_router, tags=["Auth"])
app.include_router(category_router, tags=["Category"])
# app.include_router(society_router, tags=["Society"])
# app.include_router(product_router,tags=["Products"])
# app.include_router(order_router,tags=["Orders"])
# app.include_router(buy_request_router, tags=["Buy-Request"])
# app.include_router(return_request_router,tags=["Return-Request"])
# app.include_router(feedback_router,tags=["Feedback"])
# app.include_router(user_router,tags=["User"])