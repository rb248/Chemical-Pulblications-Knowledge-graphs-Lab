from typing import Annotated

from fastapi import UploadFile, File
from pydantic import Field, BaseModel

ImageClassificationUpload = Annotated[UploadFile, File(description="Image (e.g., flowsheet in PNG form) that will be classified")]


class ImageClassificationResult(BaseModel):
    class_name: str = Field(description="Resulting class of classification")
    confidence: float = Field(description="Certainty about according class")


class ImageClassificationResponse(BaseModel):
    classes: list[ImageClassificationResult] = Field(description="Classes that the provided image can be assigned to")
