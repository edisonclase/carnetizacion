from fastapi import FastAPI

app = FastAPI(title="Proyecto de Carnetizacion by Aula Nova")


@app.get("/")
def read_root():
    return {"message": "Proyecto de carnetizacion activo"}