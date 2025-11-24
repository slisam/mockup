from __future__ import annotations
from pathlib import Path
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.openapi.docs import get_swagger_ui_html, get_redoc_html
import yaml

from .core.config import settings
from .api.routes.transformations import router as transformations_router


SPEC_FILE = Path(__file__).parent / 'openapi' / 'swagger_rc_v1.1.1.yml'
if SPEC_FILE.exists():
    with open(SPEC_FILE, 'r', encoding='utf-8') as f:
        OPENAPI_SPEC = yaml.safe_load(f)
else:
    OPENAPI_SPEC = {'openapi':'3.0.3','info':{'title':settings.PROJECT_NAME,'version':settings.PROJECT_VERSION},'paths':{}}

app = FastAPI(title=settings.PROJECT_NAME, version=settings.PROJECT_VERSION, docs_url=None, redoc_url=None, openapi_url='/openapi.json')

app.add_middleware(
    CORSMiddleware,
    allow_origins=[o.strip() for o in settings.CORS_ORIGINS.split(',') if o.strip()] if settings.CORS_ORIGINS else ['*'],
    allow_credentials=True,
    allow_methods=['*'],
    allow_headers=['*'],
)

app.include_router(transformations_router)

@app.get('/docs', include_in_schema=False)
async def custom_swagger_ui():
    return get_swagger_ui_html(openapi_url=app.openapi_url, title=f"{app.title} - Swagger UI")

@app.get('/redoc', include_in_schema=False)
async def custom_redoc():
    return get_redoc_html(openapi_url=app.openapi_url, title=f"{app.title} - ReDoc")

app.openapi = lambda: OPENAPI_SPEC  # type: ignore

@app.get('/', include_in_schema=False)
async def root():
    return {'status':'ok','service':app.title,'version':app.version}
