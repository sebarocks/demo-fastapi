from typing import Optional
from fastapi import FastAPI, HTTPException
from fastapi.staticfiles import StaticFiles
from sqlmodel import SQLModel, Field, Session, create_engine, select

app = FastAPI()


#BaseModel->SQLModel<-Model(sqlalchemy)

class Perro(SQLModel, table=True):
    id: Optional[int] = Field(default=None, primary_key=True)
    nombre: str
    raza: str
    edad: int


sqlite_file_name = "database.db"
sqlite_url = f"sqlite:///{sqlite_file_name}"
engine = create_engine(sqlite_url, echo=True)

#SQLModel.metadata.create_all(engine)

app.mount("/files", StaticFiles(directory="files"), name="files")

@app.get('/')
def inicio():
    return {
        'saludo':'hola',
        'emisor':'Seba'
    }

@app.get('/saludo/{nombre}')
def saludo(nombre: str):
    return f"hola {nombre.capitalize()}"

@app.post('/perro/add/')
def put_perro(perrito:Perro):
    with Session(engine) as session:
        session.add(perrito)
        session.commit()
        session.refresh(perrito)
        return perrito

@app.get('/perros/')
def all_perros():
    with Session(engine) as session:
        query = select(Perro)
        perros = session.exec(query).all()
        return perros

@app.get('/perros/{perro_id}')
def read_perro(perro_id : int):
    with Session(engine) as session:
        perro = session.get(Perro, perro_id)
        if not perro:
            raise HTTPException(status_code=404, detail="Perro not found")
        return perro

@app.delete('/perros/{perro_id}')
def delete_perro(perro_id: int):
    with Session(engine) as session:
        perro = session.get(Perro, perro_id)
        if not perro:
            raise HTTPException(status_code=404, detail="Perro not found")
        session.delete(perro)
        session.commit()
        return {'ok':True, 'operation':f"Perro {perro_id} eliminado... de la BD"}

@app.patch('/perros/{perro_id}')
def update_perro(perro_id: int, perro : Perro):
    with Session(engine) as session:
        db_perro = session.get(Perro, perro_id)
        if not db_perro:
            raise HTTPException(status_code=404, detail="Perro not found")
        
        perro_data = perro.dict(exclude_unset=True)
        for key, value in perro_data.items():
            setattr(db_perro, key, value)
        
        session.add(db_perro)
        session.commit()
        session.refresh(db_perro)
        return db_perro