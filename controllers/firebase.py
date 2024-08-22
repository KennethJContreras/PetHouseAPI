import os
import requests
import json
import logging
import traceback

from dotenv import load_dotenv
from fastapi import HTTPException, Depends


import firebase_admin
from firebase_admin import credentials, auth as firebase_auth
from models.UserLogin import UserLogin
from utils.database import fetch_query_as_json, get_db_connection
from utils.security import create_jwt_token
from models.UserRegister import UserRegister

# Configurar logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()


# Inicializar la app de Firebase Admin
cred = credentials.Certificate("secrets/admin_firebase.json")
firebase_admin.initialize_app(cred)

async def register_user_firebase(user: UserRegister):
    user_record = {}
    try:
        # Crear usuario en Firebase Authentication
        user_record = firebase_auth.create_user(
            email=user.email,
            password=user.password
        )

    except Exception as e:
        print(e)
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar usuario: {e}"
        )

    query = f""" EXEC ph.SP_CreateUser 
        @IdUsuario = {user_record.uid}, 
        @nombre = '{user.firstname}', 
        @apellido = '{user.lastname}', 
        @correo = '{user.email}', 
        @IdMunicipio = {user.IdMunicipio}, 
        @telefono = '{user.phone}', 
        @fechaNacimiento = '{user.birthdate}', 
        @idPlan = {user.IdPlan}"""

    result = {}
    
    try:

        result_json = await fetch_query_as_json(query, is_procedure=True)
        ##result = json.loads(result_json)[0]

        return {"message": "Usuario registrado exitosamente"}

    except Exception as e:
        firebase_auth.delete_user(user_record.uid)
        raise HTTPException(status_code=500, detail=str(e))
    
async def login_user_firebase(user: UserLogin):
    try:
        print(f"Email recibido: {user.email}, Tipo: {type(user.email)}")
        print(f"Password recibido: {user.password}, Tipo: {type(user.password)}")

        api_key = os.getenv("FIREBASE_API_KEY")
        url = f"https://identitytoolkit.googleapis.com/v1/accounts:signInWithPassword?key={api_key}"
        payload = {
            "email": user.email,
            "password": user.password,
            "returnSecureToken": True
        }
        response = requests.post(url, json=payload)
        response_data = response.json()

        print("Respuesta Firebase:", response_data)

        if "error" in response_data:
            raise HTTPException(
                status_code=400,
                detail=f"Error al autenticar usuario: {response_data['error']['message']}"
            )

        query = """
            SELECT
                Correo,
                PrimerNombre,
                PrimerApellido
            FROM [ph].[Usuarios]
            WHERE Correo = ?
        """

        try:
            params = (user.email,)
            result_json = await fetch_query_as_json(query, params)
            print("Resultado de la consulta:", result_json)
            result_dict = json.loads(result_json)
            print("Diccionario resultante:", result_dict)

            if not result_dict:
                raise HTTPException(status_code=404, detail="Usuario no encontrado")

            # Asegurarse de que todos los valores sean cadenas
            nombre = str(result_dict[0]["PrimerNombre"])
            apellido = str(result_dict[0]["PrimerApellido"])
            email = str(user.email)

            return {
                "message": "Usuario autenticado exitosamente",
                "idToken": create_jwt_token(nombre, apellido, email)
            }
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    except Exception as e:
        error_detail = {
            "type": type(e).__name__,
            "message": str(e),
            "traceback": traceback.format_exc()
        }
        print("Error:", error_detail)
        raise HTTPException(
            status_code=400,
            detail=f"Error al registrar usuario: {error_detail}"
        )
 