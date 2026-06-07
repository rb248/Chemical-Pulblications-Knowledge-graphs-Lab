from fastapi import APIRouter, HTTPException
from starlette.exceptions import HTTPException

from app import schemes
from app.models.ImageClassification.meta_data.model_info import model_info_obj as img_classification_model_info

router = APIRouter(
    prefix="/img_classification",
    tags=["Image Classification"]
)


@router.get(
    '/info',
    response_model=schemes.ModelInfo,
    description="Get information about the ML model used for image classification",
    tags=["Image Classification"]
)
async def get_info_for_img_classification():
    return img_classification_model_info


@router.post(
    '/get_class',
    description="Identify the images in a provided PDF",
    tags=["Image Classification"],
    response_model=schemes.ImageClassificationResponse,
    responses={
        400: {"description": "Bad Request, e.g., because the wrong file type has been provided."}
    }
)
async def classify_img(img_file: schemes.ImageClassificationUpload):
    if img_file.content_type != "image/png":
        raise HTTPException(status_code=400, detail="Provided file has wrong type: Input file must be provided as a PNG.")

    return schemes.ImageClassificationResponse(classes=[
        schemes.ImageClassificationResult(class_name="cat", confidence=0.98)
    ])
