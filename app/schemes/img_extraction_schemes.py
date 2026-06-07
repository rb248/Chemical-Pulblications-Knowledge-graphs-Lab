from typing import Annotated

from fastapi import UploadFile, File
from pydantic import BaseModel, Field

ImageIdentificationUpload = Annotated[UploadFile, File(description="Publication (PDF) from which images will be extracted")]


class PositionOnPage(BaseModel):
    x: int = Field(description="Vertical pixel value of Position")
    y: int = Field(description="Horizontal pixel value of Position")


class ImageBorder(BaseModel):
    page: int = Field(description="The page on which the image is")
    startPos: PositionOnPage = Field(description="Top left position, where image starts")
    endPos: PositionOnPage = Field(description="Bottom right position, where image ends")


class ImageBorders(BaseModel):
    imgs: list[ImageBorder] = Field(description="A list of all images represented as Image Borders found in the provided PDF")
