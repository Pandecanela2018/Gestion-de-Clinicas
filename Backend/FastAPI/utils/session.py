from itsdangerous import URLSafeSerializer
from fastapi import Request, Response

SECRET_KEY = "CAMBIA_ESTE_SECRETO"

serializer = URLSafeSerializer(SECRET_KEY)

def set_session(response: Response, data: dict):
    session_data = serializer.dumps(data)
    response.set_cookie("session", session_data, httponly=True)

def get_session(request: Request):
    cookie = request.cookies.get("session")
    if cookie:
        try:
            return serializer.loads(cookie)
        except:
            return None
    return None

def clear_session(response: Response):
    response.delete_cookie("session")
