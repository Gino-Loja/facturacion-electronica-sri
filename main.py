# -*- coding: utf-8 -*-
from contextlib import asynccontextmanager
from app.lib.conexion.pool import db_manager_instance
from app.routes.invoice import routerInvoice
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

#app = FastAPI()

@asynccontextmanager
async def lifespan(app: FastAPI):

    #ftp: Optional[ftplib.FTP] = conexion_ftp()
    # device = 'cuda' if torch.cuda.is_available() else 'cpu'
    # model = YOLO('Modelos/best.pt').to(device)
    #app.ftp = ftp
    # conexion = get_db_connection()
    # app.conexion = conexion

    print('db_manager_instance._initialize_pool()')
    db_manager_instance._initialize_pool()
    yield
    print('finalizando')
    db_manager_instance.close_pool()
    #cerrar_conexion_ftp(ftp)
origins = [
    "*"
]
app = FastAPI(lifespan=lifespan)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],  # URL de tu frontend
    allow_credentials=True,
    allow_methods=["*"],  # Permite todos los métodos
    allow_headers=["*"],  # Permite todos los headers
)



app.include_router(router=routerInvoice)
