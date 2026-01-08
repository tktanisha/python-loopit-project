class ApiPaths:
    HEALTH = "/health"
    AUTH_SIGNUP = "/auth/register"
    AUTH_LOGIN = "/auth/login"

    CREATE_CATEGORY= "/categories"
    GET_CATEGORY= "/categories"
    UPDATE_CATEGORY= "/categories/{id}"
    DELETE_CATEGORY= "/categories/{id}"

    CREATE_SOCIETY= "/societies"
    GET_SOCIETY= "/societies"
    UPDATE_SOCIETY= "/societies/{id}"
    DELETE_SOCIETY= "/societies/{id}"
    
    GET_PRODUCTS = "/products"
    GET_PRODUCT_BY_ID = "/products/{id}"
    CREATE_PRODUCT = "/products/create"
    UPDATE_PRODUCT = "/products/{id}/update"
    DELETE_PRODUCT = "/products/{id}/delete"

    GET_ORDER_HISTORY = "/orders/history"
    RETURN_ORDER = "/orders/{orderId}/return"
    GET_APPROVED_AWAITING_ORDERS = "/orders/approved-awaiting"
    GET_LENDER_ORDERS = "/orders/lender"

    CREATE_BUYER_REQUEST = "/buyer-requests"
    GET_BUYER_REQUESTS = "/buyer-requests"
    UPDATE_BUYER_REQUEST_STATUS = "/buyer-requests/{requestId}/update"

    CREATE_RETURN_REQUEST = "/return-requests"
    GET_RETURN_REQUESTS = "/return-requests"
    UPDATE_RETURN_REQUEST_STATUS = "/return-requests/{requestId}/update"

    CREATE_FEEDBACK = "/feedbacks"
    GET_GIVEN_FEEDBACKS = "/feedbacks/given"
    GET_RECEIVED_FEEDBACKS = "/feedbacks/received"

    BECOME_LENDER = "/users/become-lender"
    GET_USERS = "/users"
    GET_USER_BY_ID = "/users/{id}"
    DELETE_USER_BY_ID = "/users/{id}"


