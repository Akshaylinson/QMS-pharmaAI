from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models.complaint import Complaint
from app.api.routes import router
app=FastAPI(title='AIVOA QMS API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup(): Base.metadata.create_all(bind=engine)
app.include_router(router,prefix='/api')
@app.get('/health')
def health(): return {'status':'ok'}
