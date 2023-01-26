import os

from fastapi import FastAPI, Request, status
from fastapi.encoders import jsonable_encoder
from fastapi.exceptions import RequestValidationError
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from app.common.errors import OrkgSimCompApiError
from app.common.util import io
from app.db.connection import Base, engine
from app.routers import contribution, shortener, storage

_registered_services = []


def create_app():
    app = FastAPI(
        title='ORKG-SimComp-API',
        root_path=os.getenv('ORKG_SIMCOMP_API_PREFIX', ''),
        servers=[
            {'url': os.getenv('ORKG_SIMCOMP_API_PREFIX', ''), 'description': ''}
        ],
    )

    _configure_app_routes(app)
    _configure_exception_handlers(app)
    _configure_cors_policy(app)
    _create_database_tables()
    _save_openapi_specification(app)

    return app


def _configure_app_routes(app):
    app.include_router(contribution.router)
    app.include_router(shortener.router)
    app.include_router(storage.router)


def _configure_exception_handlers(app):

    async def validation_exception_handler(request: Request, exc: RequestValidationError):
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content=jsonable_encoder({"detail": exc.errors(), "body": exc.body}),
        )

    async def orkg_simcomp_api_exception_handler(request: Request, exc: OrkgSimCompApiError):
        return JSONResponse(
            status_code=exc.status_code,
            content=jsonable_encoder({
                'location': exc.class_name,
                'detail': exc.detail
            })
        )

    app.add_exception_handler(RequestValidationError, validation_exception_handler)
    app.add_exception_handler(OrkgSimCompApiError, orkg_simcomp_api_exception_handler)


def _configure_cors_policy(app):
    app.add_middleware(
        CORSMiddleware,
        allow_origins='*',
        allow_methods=["*"],
        allow_headers=["*"],
        allow_credentials=False
    )


def _create_database_tables():
    if os.environ.get('ORKG_SIMCOMP_API_ENV') != 'test':
        Base.metadata.create_all(bind=engine)


def _save_openapi_specification(app):
    app_dir = os.path.dirname(os.path.realpath(__file__))
    io.write_json(app.openapi(), os.path.join(app_dir, '..', 'openapi.json'))
