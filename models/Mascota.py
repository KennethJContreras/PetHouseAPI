from pydantic import BaseModel, Field, validator

class PetForm(BaseModel):
    nombre: str
    edad: int
    raza: int
    detalles: str

    @validator('nombre')
    def validar_nombre(cls, value):
        if not value or len(value.strip()) == 0:
            raise ValueError('El nombre no puede estar vacío')
        return value

    @validator('edad')
    def validar_edad(cls, value):
        if value <= 0:
            raise ValueError('La edad debe ser un número positivo')
        return value


    @validator('raza')
    def validar_raza(cls, value):
        if value <= 0:
            raise ValueError('La edad debe ser un número positivo')
        return value

    @validator('detalles')
    def validar_detalles(cls, value):
        if value and len(value) > 1000:
            raise ValueError('Los detalles deben tener menos de 1000 caracteres')
        return value
