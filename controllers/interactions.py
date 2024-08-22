import json
import logging

from fastapi import HTTPException


from utils.database import fetch_query_as_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

async def fetch_historias(email: str):
    query = f"""EXEC ph.SP_GetHistorias @email = '{ email }'"""
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
async def create_story(historia, correo):
    query = f"""EXEC ph.SP_CreateStory @correo = '{correo}', @descripcion = '{historia.descripcion}'"""

    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query, is_procedure=True)
        result_dict = json.loads(result_json)
        print(result_dict)
        return result_dict
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))
    
async def give_like(id, correo):
    query = f"""EXEC ph.SP_GiveLike @correo = '{correo}', @idhistoria = '{id}'"""

    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query, is_procedure=True)
        result_dict = json.loads(result_json)
        print(result_dict)
        return result_dict
    except Exception as e:
        print("error", e)
        raise HTTPException(status_code=500, detail=str(e))