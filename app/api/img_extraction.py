from fastapi import APIRouter, HTTPException, Form
from fastapi.responses import FileResponse

from app import schemes
from app.models.ImageDetection.meta_data.model_info import model_info_obj as img_detection_model_info

router = APIRouter(
    prefix="/img_detection",
    tags=["Image Extraction"]
)


@router.get(
    '/info',
    description="Get information about the ML model used for image detection in the PDF files",
    tags=["Image Extraction"],
    response_model=schemes.ModelInfo
)
async def get_info_for_img_detection():
    return img_detection_model_info


@router.post(
    '/identify_imgs',
    description="Identify the images in a provided PDF",
    tags=["Image Extraction"],
    response_model=schemes.ImageBorders,
    responses={
        400: {"description": "Bad Request, e.g., because the wrong file type has been provided."}
    }
)
async def identify_imgs_in_pdf(pdf_file: schemes.ImageIdentificationUpload):
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Provided file has wrong type: Input file must be provided as a PDF.")

    return schemes.ImageBorders(imgs=[
        schemes.ImageBorder(
            page=1,
            startPos=schemes.PositionOnPage(x=0, y=0),
            endPos=schemes.PositionOnPage(x=5, y=10)
        )
    ])


@router.post(
    '/extract_img',
    description="Get the extracted image from a PDF given the page and image-border values",
    tags=["Image Extraction"],
    response_class=FileResponse,
    responses={
        200: {"description": "The cut out image"},
        400: {"description": "Bad Request, e.g., because the wrong file type has been provided."}
    }
)
async def cut_out_img_in_pdf(pdf_file: schemes.ImageIdentificationUpload, img_border: str = Form()):
    if pdf_file.content_type != "application/pdf":
        raise HTTPException(status_code=400, detail="Provided file has wrong type: Input file must be provided as a PDF.")
    
    try:
        schemes.ImageBorder.parse_raw(img_border)
    except Exception as e:
        raise HTTPException(status_code=422, detail=f"Invalid image border representation: {str(e)}")

    return FileResponse('./test/assets/test_img.png', media_type='application/octet-stream')
