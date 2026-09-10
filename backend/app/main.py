from fastapi import FastAPI
from sqlalchemy import inspect, text
from fastapi.middleware.cors import CORSMiddleware
from app.core.config import settings
from app.db.base import Base
from app.db.session import engine
from app.models.complaint import Complaint
from app.api.routes import router
app=FastAPI(title='AIVOA QMS API',version='1.0.0')
app.add_middleware(CORSMiddleware,allow_origins=[settings.frontend_origin],allow_credentials=True,allow_methods=['*'],allow_headers=['*'])
@app.on_event('startup')
def startup():
    Base.metadata.create_all(bind=engine)
    # Keep installations created before this release usable even when migrations
    # have not yet been run (Alembic remains the deployment migration path).
    additions={'originating_site':'VARCHAR(120)','impacted_materials':'VARCHAR(240)','suggested_next_action':'VARCHAR(240)','initial_risk_assessment':'TEXT'}
    existing={column['name'] for column in inspect(engine).get_columns('complaints')}
    with engine.begin() as connection:
        for name, definition in additions.items():
            if name not in existing:
                connection.execute(text(f'ALTER TABLE complaints ADD COLUMN {name} {definition}'))
app.include_router(router,prefix='/api')
@app.get('/health')
def health(): return {'status':'ok'}
