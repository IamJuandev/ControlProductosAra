from fastapi import FastAPI, HTTPException, Depends
from sqlalchemy import Column, Integer, String, Date, create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, Session
from pydantic import BaseModel
from datetime import date
from fastapi.middleware.cors import CORSMiddleware
# ----------------------
# Configuración DB
# ----------------------
SQLALCHEMY_DATABASE_URL = "sqlite:///./articulos.db"  # Persistente en archivo
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

# ----------------------
# Modelo de Base de Datos
# ----------------------
class ArticuloDB(Base):
    __tablename__ = "articulos"

    id = Column(Integer, primary_key=True, index=True)
    nombre = Column(String, index=True, nullable=False)
    fecha_retiro = Column(Date, nullable=False)
    unidades = Column(Integer, nullable=False)
    codigo_sap = Column(String, nullable=False)

Base.metadata.create_all(bind=engine)

# ----------------------
# Schemas Pydantic
# ----------------------
class ArticuloBase(BaseModel):
    nombre: str
    fecha_retiro: date
    unidades: int
    codigo_sap: str

class ArticuloCreate(ArticuloBase):
    pass

class Articulo(ArticuloBase):
    id: int

    class Config:
        orm_mode = True

# ----------------------
# FastAPI app
# ----------------------
app = FastAPI(title="API CRUD de Artículos")

# Dependencia DB
def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ----------------------
# CRUD Endpoints
# ----------------------
@app.post("/articulos/", response_model=Articulo)
def crear_articulo(articulo: ArticuloCreate, db: Session = Depends(get_db)):
    db_articulo = ArticuloDB(**articulo.dict())
    db.add(db_articulo)
    db.commit()
    db.refresh(db_articulo)
    return db_articulo

@app.get("/articulos/", response_model=list[Articulo])
def listar_articulos(db: Session = Depends(get_db)):
    return db.query(ArticuloDB).all()

@app.get("/articulos/{articulo_id}", response_model=Articulo)
def obtener_articulo(articulo_id: int, db: Session = Depends(get_db)):
    articulo = db.query(ArticuloDB).filter(ArticuloDB.id == articulo_id).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    return articulo

@app.put("/articulos/{articulo_id}", response_model=Articulo)
def actualizar_articulo(articulo_id: int, datos: ArticuloCreate, db: Session = Depends(get_db)):
    articulo = db.query(ArticuloDB).filter(ArticuloDB.id == articulo_id).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    for key, value in datos.dict().items():
        setattr(articulo, key, value)
    db.commit()
    db.refresh(articulo)
    return articulo

@app.delete("/articulos/{articulo_id}")
def eliminar_articulo(articulo_id: int, db: Session = Depends(get_db)):
    articulo = db.query(ArticuloDB).filter(ArticuloDB.id == articulo_id).first()
    if not articulo:
        raise HTTPException(status_code=404, detail="Artículo no encontrado")
    db.delete(articulo)
    db.commit()
    return {"message": "Artículo eliminado correctamente"}

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # puedes poner ["http://localhost:3000"] si usas React/Vue
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)