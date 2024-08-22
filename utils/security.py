import os
import secrets
import hashlib
import base64
import jwt

from datetime import datetime, timedelta
from fastapi import HTTPException
from dotenv import load_dotenv
from jwt import PyJWTError
from functools import wraps

load_dotenv()

SECRET_KEY = os.getenv("SECRET_KEY")
""" SECRET_KEY_FUNC = os.getenv("SECRET_KEY_FUNC")
 """
def generate_pkce_verifier():
    return secrets.token_urlsafe(32)

def generate_pkce_challenge(verifier):
    digest = hashlib.sha256(verifier.encode()).digest()
    return base64.urlsafe_b64encode(digest).rstrip(b'=').decode('ascii')


# Función para crear un JWT
def create_jwt_token(firstname:str, lastname:str, email: str):
    print("secret_key", SECRET_KEY)
    expiration = datetime.utcnow() + timedelta(hours=1)  # El token expira en 1 hora
    token = jwt.encode(
        {
            "firstname": firstname,
            "lastname": lastname,
            "email": email,
            "exp": expiration,
            "iat": datetime.utcnow()
        },
        SECRET_KEY,
        algorithm="HS256"
    )
    print("token", token)
    return token

def validate(func):
    @wraps(func)
    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=400, detail="Authorization header missing")


        scheme, token = authorization.split()
        if scheme.lower() != "bearer":
            raise HTTPException(status_code=400, detail="Invalid authentication scheme")

        try:
            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])


            email = payload.get("email")
            expired = payload.get("exp")
            firstname = payload.get("firstname")
            lastname = payload.get("lastname")


            """ falta active """
            if email is None or expired is None:
                raise HTTPException(status_code=400, detail="Invalid token")

            if datetime.utcfromtimestamp(expired) < datetime.utcnow():
                raise HTTPException(status_code=401, detail="Expired token")

            # Inyectar el email en el objeto request
            request.state.email = email
            request.state.firstname = firstname
            request.state.lastname = lastname
        except PyJWTError:
            raise HTTPException(status_code=401, detail="Invalid token or expired token")



        return await func(*args, **kwargs)
    return wrapper

    async def wrapper(*args, **kwargs):
        request = kwargs.get('request')
        if not request:
            raise HTTPException(status_code=400, detail="Request object not found")

        authorization: str = request.headers.get("Authorization")
        if not authorization:
            raise HTTPException(status_code=403, detail="Authorization header missing")

        try:
            scheme, token = authorization.split()
            if scheme.lower() != "bearer":
                raise HTTPException(status_code=403, detail="Invalid authentication scheme")

            payload = jwt.decode(token, SECRET_KEY, algorithms=["HS256"])

            email = payload.get("email")
            expired = payload.get("exp")
            active = payload.get("active")
            if email is None or expired is None or active is None:
                raise HTTPException(status_code=403, detail="Invalid token")

            if datetime.utcfromtimestamp(expired) < datetime.utcnow():
                raise HTTPException(status_code=403, detail="Expired token")

            if not active:
                raise HTTPException(status_code=403, detail="Inactive user")

            # Inyectar el email en el objeto request
            request.state.email = email
        except PyJWTError:
            raise HTTPException(status_code=403, detail="Invalid token or expired token")

        return await func(*args, **kwargs)
    return wrapper