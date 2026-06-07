from fastapi import FastAPI
from fastapi.openapi.utils import get_openapi

from .api import img_classification, img_extraction


def custom_openapi():
    if application.openapi_schema:
        return application.openapi_schema
    openapi_schema = get_openapi(
        title="ModelZoo",
        description="Interaction with machine learning models for chemical engineering",
        version="beta_00",
        routes=application.routes
    )
    application.openapi_schema = openapi_schema
    return application.openapi_schema


def get_tags():
    return [
        {
            "name": "root"
        },
        {
            "name": "Image Detection",
            "description": "Endpoints for machine learning model extracting images from a PDF"
        },
        {
            "name": "Image Classification",
            "description": "Endpoints for machine learning model classifying provided images"
        }
    ]


application = FastAPI(docs_url="/documentation", redoc_url=None, openapi_tags=get_tags())
application.openapi = custom_openapi

application.include_router(img_classification.router)
application.include_router(img_extraction.router)


@application.get(
    '/',
    response_model=str,
    description="Default route for testing whether API is up",
    tags=["root"]
)
async def root():
    return 'Hello! This is an API which applies machine learning models for chemical engineering.'
