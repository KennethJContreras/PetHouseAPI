import json
import logging
import aiofiles
import os

from fastapi import HTTPException, UploadFile, File

from utils.database import fetch_query_as_json

from azure.storage.blob import BlobServiceClient, generate_blob_sas, BlobSasPermissions

from datetime import datetime, timedelta
from dotenv import load_dotenv

from utils.database import fetch_query_as_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

AZURE_STORAGE_CONNECTION_STRING = os.getenv("AZURE_SAK")
AZURE_STORAGE_CONTAINER = os.getenv("AZURE_STORAGE_CONTAINER")

blob_service_client = BlobServiceClient.from_connection_string(AZURE_STORAGE_CONNECTION_STRING)

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

    
async def fetch_animales():
    query = "SELECT IdAnimal AS Id, Descripcion FROM ph.Animales"
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_mascotas_filtradas(idAnimal: int, idRaza: int, idColor: int):
    query = "SELECT M.IdMascota, M.Nombre, M.Detalles, M.Edad, R.Descripcion AS Raza, MU.Descripcion AS MunicipioDescripcion FROM ph.Mascotas M LEFT JOIN ph.MascotasColores MC ON MC.IdMascota = M.IdMascota INNER JOIN ph.Razas R ON R.IdRaza = M.IdRaza INNER JOIN ph.Animales A ON A.IdAnimal = R.IdAnimal INNER JOIN ph.Usuarios U ON M.IdDuenio = U.IdUsuario INNER JOIN ph.Municipios MU ON U.IdMunicipio = MU.IdMunicipio WHERE 1=1"

    if idRaza != 0:
        query += f" AND M.IdRaza = {idRaza}"
    if idColor != 0:
        query += f" AND MC.IdColor = {idColor}"
    if idAnimal != 0:
        query += f" AND A.IdAnimal = {idAnimal}"
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        print("resss",result_dict)
        return result_dict
    
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_mascotas(correo):
    sas_expiration = datetime.utcnow() + timedelta(minutes=2)

    query = f"""EXEC ph.SP_GetPetsInfo @correo = '{correo}'"""
                
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        
        print("resultdict",result_dict)
        for file in result_dict:
            file_name = f"{ file['IdMascota'] }/{ file['NombreImagen'] }"
            # Genera el SAS
            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=AZURE_STORAGE_CONTAINER,
                blob_name=file_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=sas_expiration
            )
            
            if file['NombreImagen'] != None:
                file["url"] = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER}/{file_name}?{sas_token}"
            
        return result_dict
    
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))    
async def fetch_mascotas_usuario(correo):
    sas_expiration = datetime.utcnow() + timedelta(minutes=2)
    
    query = f"""SELECT M.IdMascota, M.Detalles, MI.NombreImagen, M.Edad, R.Descripcion AS Raza, M.Nombre FROM ph.Mascotas M
    INNER JOIN ph.Razas R ON M.IdRaza = R.IdRaza
    LEFT JOIN ph.Mascotas_Imagenes MI ON M.IdMascota = MI.IdMascota
    WHERE M.IdDuenio = (SELECT IdUsuario FROM ph.Usuarios WHERE Correo = '{correo}')"""
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        
        print("resultdict",result_dict)
        for file in result_dict:
            file_name = f"{ file['IdMascota'] }/{ file['NombreImagen'] }"
            # Genera el SAS
            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=AZURE_STORAGE_CONTAINER,
                blob_name=file_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=sas_expiration
            )

            if file['NombreImagen'] != None:
                file["url"] = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER}/{file_name}?{sas_token}"
                        
        return result_dict
    
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_razas_de_animal(id_animal: int):
    query = f"""SELECT IdRaza AS Id, Descripcion FROM ph.Razas WHERE IdAnimal = {id_animal}"""
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_colores_de_animales():
    query = f"""SELECT IdColor AS Id, Descripcion FROM ph.Colores C"""
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_mascotas_por_raza(id_raza: int):
    query = f"""EXEC ph.SP_GetPetsInfo @idRaza = {id_raza}"""
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_mascotas_por_filtro(animal: int = 0 ,raza: int = 0, color: int = 0):
    query = f"""EXEC ph.SP_GetPetsInfo @idAnimal = {animal}, @idRaza = {raza}, @idColor = {color}"""

            
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_mascota(id_animal: int):
    sas_expiration = datetime.utcnow() + timedelta(minutes=2)

    query = f"""EXEC ph.SP_GetPetDetail @idMascota = {id_animal}"""

    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        
        for file in result_dict:
            file_name = f"{ file['IdMascota'] }/{ file['NombreImagen'] }"
            # Genera el SAS
            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=AZURE_STORAGE_CONTAINER,
                blob_name=file_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=sas_expiration
            )
            
            if file['NombreImagen'] != None:
                file["url"] = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER}/{file_name}?{sas_token}"

        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def create_mascota(mascota, correo):
    query = f"""EXEC ph.SP_CreatePet @correo = '{correo}', @idRaza = {mascota.raza}, @nombre = {mascota.nombre}, @edad = {mascota.edad}, @detalles = {mascota.detalles}"""

    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query, is_procedure=True)
        result_dict = json.loads(result_json)
        print(result_dict)
        return result_dict
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
async def update_mascota(id, mascota):
    query = f"""EXEC ph.SP_UpdatePet @idMascota = {id}, @nombre = {mascota.nombre}, @edad = {mascota.edad}, @detalles = {mascota.detalles}"""

    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query, is_procedure=True)
        result_dict = json.loads(result_json)
        print(result_dict)
        return result_dict
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_upload_pet_images( email: str, id: int, images: list[UploadFile] = File(...) ):
    try:
        for file in images:

            query = f" exec ph.SP_insert_pet_images @idMascota = {id}, @nombreImagen = '{file.filename}', @correo = '{email}'"
            result_json = await fetch_query_as_json(query, is_procedure=True)
            result = json.loads(result_json)[0]

            if result["status"] != 200:
                raise HTTPException(status_code=404, detail="Pet not found")

            container_client = blob_service_client.get_blob_client(container=AZURE_STORAGE_CONTAINER, blob=f"{id}/{file.filename}")
            async with aiofiles.open(file.filename, 'wb') as f:
                await f.write(await file.read())
            with open(file.filename, "rb") as data:
                container_client.upload_blob(data, overwrite=True)


        return {"message": "File uploaded successfully"}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_download_card_files(id: int):
    sas_expiration = datetime.utcnow() + timedelta(minutes=2)

    query = f"""
        select
            id
            , card_id
            , file_name
            , cast(created_at as nvarchar(100)) as created_at
        from otd.card_files
        where card_id = {id}
    """

    try:
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)

        for file in result_dict:
            file_name = f"{ file['card_id'] }/{ file['file_name'] }"
            # Genera el SAS
            sas_token = generate_blob_sas(
                account_name=blob_service_client.account_name,
                container_name=AZURE_STORAGE_CONTAINER,
                blob_name=file_name,
                account_key=blob_service_client.credential.account_key,
                permission=BlobSasPermissions(read=True),
                expiry=sas_expiration
            )
            
            if file['NombreImagen'] != None:
                file["url"] = f"https://{blob_service_client.account_name}.blob.core.windows.net/{AZURE_STORAGE_CONTAINER}/{file_name}?{sas_token}"

        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

    