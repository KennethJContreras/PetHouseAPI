import json
import logging

from fastapi import HTTPException


from utils.database import fetch_query_as_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


    
async def fetch_departamentos():
    query = "SELECT IdDepartamento, Descripcion FROM ph.Departamentos"
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
async def fetch_municipios(id: int):
    query = f"""SELECT IdMunicipio, Descripcion FROM ph.Municipios WHERE IdDepartamento = {id}"""
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    
