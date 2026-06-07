from datetime import date

from pydantic import BaseModel, Field


class ModelInfo(BaseModel):
    name: str = Field(description="Name of the ML model")
    modelVersion: str
    date: date
    author: list[str] = Field(description="Authors of the ML model code")
    references: list[str] = Field(description="E.g., publication for the ML model")

