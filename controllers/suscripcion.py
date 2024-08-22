import json
import logging

from fastapi import HTTPException


from utils.database import fetch_query_as_json

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


    
async def fetch_planes_de_suscripcion():
    query = "SELECT IdPlan, NombrePlan, CONVERT(VARCHAR(10), Precio) AS Precio, Detalles FROM ph.PlanesDeSuscripcion"
        
    try:
        logger.info(f"QUERY LIST")
        result_json = await fetch_query_as_json(query)
        result_dict = json.loads(result_json)
        return result_dict
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
    