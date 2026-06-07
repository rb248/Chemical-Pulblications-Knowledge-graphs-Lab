from datetime import date

from app.schemes.model_info_scheme import ModelInfo

model_info_obj = ModelInfo(
    name="Image extraction model", modelVersion="v_01", date=date(2021, 7, 21),
    author=["Zejiang Shen", "Ruochen Zhang", "Melissa Dell", "Benjamin Charles Germain Lee", "Jacob Carlson", "Weining Li"],
    references=["https://arxiv.org/abs/2103.15348"]
)
