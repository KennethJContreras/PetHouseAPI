from pydantic import BaseModel, Field, validator

class StoryForm(BaseModel):
    descripcion: str
    
    @validator('descripcion')
    def validar_descripcion(cls, value):
        if value and len(value) > 1000:
            raise ValueError('Las descripciones deben tener menos de 1000 caracteres')
        return value
