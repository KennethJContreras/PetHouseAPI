from fastapi import FastAPI, Request, Depends, Response, File, UploadFile

from models.Story import StoryForm
from models.UserRegister import UserRegister

from models.Mascota import PetForm

from models.MascotaDTO import MascotaDTO

from controllers.o365 import login_o365 , auth_callback_o365

from controllers.google import login_google , auth_callback_google

from controllers.firebase import register_user_firebase, login_user_firebase

from models.UserLogin import UserLogin

from utils.security import validate

from fastapi.middleware.cors import CORSMiddleware

from controllers.direction import fetch_departamentos, fetch_municipios

from controllers.suscripcion import fetch_planes_de_suscripcion

from controllers.interactions import fetch_historias, create_story, give_like

from controllers.pets import fetch_animales, fetch_razas_de_animal, fetch_mascotas_por_raza, fetch_colores_de_animales, fetch_mascotas, fetch_mascotas_filtradas, fetch_mascota, create_mascota, fetch_mascotas_usuario, update_mascota, fetch_upload_pet_images

app = FastAPI()

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Permitir todos los orígenes
    allow_credentials=True,
    allow_methods=["*"],  # Permitir todos los métodos
    allow_headers=["*"],  # Permitir todos los encabezados
)


@app.get("/login")
async def login():
    return await login_o365()

@app.get("/auth/callback")
async def authcallback(request: Request):
    return await auth_callback_o365(request)  

@app.get("/login/google")
async def logingoogle():
    return await login_google()

@app.get("/auth/google/callback")
async def authcallbackgoogle(request: Request):
    return await auth_callback_google(request)

@app.post("/register")
async def register(user: UserRegister):
    return await register_user_firebase(user)

@app.post("/login/custom")
async def login_custom(user: UserLogin):
    return await login_user_firebase(user)

@app.get("/departamentos")
async def get_departments():
    return await fetch_departamentos()

@app.get("/suscripciones")
async def get_suscripciones():
    return await fetch_planes_de_suscripcion()

@app.get("/departamentos/{id}/municipios")
async def get_municipios(id: int):
    return await fetch_municipios(id)

""" mascotas """
@app.get("/animales")
@validate
async def get_tipos_de_animales(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache"
    return await fetch_animales()

@app.get("/mascotas")
@validate
async def get_mascotas(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache"
    return await fetch_mascotas(request.state.email)

@app.post("/mascotas/{id}/imagenes")
@validate
async def upload_imagenes(request: Request, response: Response, id: int, images: list[UploadFile] = File(...) ):
    response.headers["Cache-Control"] = "no-cache"
    return await fetch_upload_pet_images( request.state.email, id, images )

@app.post("/mascotas")
@validate
async def post_mascota(request: Request, response: Response ,mascota: PetForm):
    response.headers["Cache-Control"] = "no-cache"
    print(mascota)
    return await create_mascota(mascota, request.state.email)

@app.post("/historias")
@validate
async def post_mascota(request: Request, response: Response ,historia: StoryForm):
    response.headers["Cache-Control"] = "no-cache"
    return await create_story(historia, request.state.email)

@app.post("/historias/{id}/likes")
@validate
async def post_like(request: Request, response: Response ,id: int):
    response.headers["Cache-Control"] = "no-cache"
    return await give_like(id, request.state.email)

@app.get("/mascotas-filtradas")
@validate
async def get_mascotas_filtradas(request: Request, response: Response, idAnimal: int = 0, idRaza: int = 0, idColor: int = 0):
    return await fetch_mascotas_filtradas(idAnimal, idRaza, idColor)

@app.get("/usuarios/mascotas")
@validate
async def get_mascotas_filtradas(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache"
    return await fetch_mascotas_usuario(request.state.email)

@app.get("/animales/{id}/razas")
@validate
async def get_razas_por_animal(request: Request, response: Response, id: int):
    return await fetch_razas_de_animal(id)

@app.get("/razas/{id}/mascotas")
@validate
async def get_mascotas_por_raza(request: Request, response: Response, id: int):
    return await fetch_mascotas_por_raza(id)

@app.get("/razas/{id}/")
@validate
async def get_mascotas_por_raza(request: Request, response: Response, id: int):
    response.headers["Cache-Control"] = "no-cache"
    return await fetch_mascotas_por_raza(id)

@app.get("/colores")
@validate
async def get_colores(request: Request, response: Response, ):
    response.headers["Cache-Control"] = "no-cache"
    return await fetch_colores_de_animales()
 
@app.get("/mascotas/{id}")
@validate
async def get_mascota(request: Request, response: Response, id: int):
    response.headers["Cache-Control"] = "no-cache"
    return await fetch_mascota(id)

@app.put("/mascotas/{id}")
@validate
async def get_mascota(request: Request, response: Response, id: int, mascota: MascotaDTO):
    response.headers["Cache-Control"] = "no-cache"
    return await update_mascota(id, mascota)

@app.get("/historias")
@validate
async def get_historias(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache"
    return await fetch_historias(request.state.email)

@app.get("/user")
@validate
async def user(request: Request, response: Response):
    response.headers["Cache-Control"] = "no-cache";
    return {
        "email": request.state.email
        , "firstname": request.state.firstname
        , "lastname": request.state.lastname
    }


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)